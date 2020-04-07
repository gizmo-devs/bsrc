from flask import (
    Blueprint, redirect, render_template, request, url_for
)
import json
from ..core.db import get_db, query_db

bp = Blueprint('team', __name__, url_prefix='/teams')


@bp.route('/')
def index():
    teams = query_db(
        'SELECT DISTINCT id, team_name, team_size, season'
        ' FROM {|schema|}.team', ())

    teamData = []

    for team in teams:
        users = query_db(
            'SELECT usr.id, usr.first_name, usr.surname, tm.submitted_avg'
            ' FROM {|schema|}.user as usr'
            ' join {|schema|}.teamMembers AS tm ON user_id=usr.id'
            ' AND team_id=%s', [str(team['id'])])
        active_comps = query_db(
            'SELECT competition_name, id FROM {|schema|}.competitions WHERE id IN '
            '(SELECT competition_id FROM {|schema|}.compTeam WHERE team_id=%s)', str(team['id'])
        )
        avgs = query_db("""SELECT
        ROUND(AVG(result),2) as curr_avg
        , user_id
        --, competition_id
        FROM {|schema|}.scores
        group by user_id
        having user_id in
            (
            SELECT
                user_id
            FROM {|schema|}.teamMembers
            WHERE team_id=%s
            );""", [team['id']])

        teaminfo = {
            "details" : team,
            "avgs" : avgs,
            "active_comps" : active_comps,
            "members" : users
        }
        teamData.append(teaminfo)
    #print("PRINTING TEAM DATA")
    #print (teamData)

    return render_template('postal/teams.html', teams=teamData)


@bp.route('/create', methods=('GET', 'POST'))
def team_create():
    db = get_db()
    users = query_db('SELECT id, first_name, surname FROM {|schema|}.user', [])
    if request.method == 'POST':
        print("Creating Team")
        team_name = request.form['team_name']
        team_size = request.form['team_size']
        season = request.form.get('season')

        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO team (team_name, team_size, season) VALUES (?, ?, ?)',
            (team_name, team_size, season)
        )
        db.commit()

        team_id = cursor.lastrowid
        print("new team id", team_id)
        return redirect(url_for('team.team_edit', id=team_id))

    return render_template('postal/create_team.html', users=users)

@bp.route('/edit/<int:id>' , methods=('GET', 'POST'))
def team_edit(id):
    db = get_db()
    users = db.execute('SELECT id, first_name, surname FROM user').fetchall()
    db.commit()
    if request.method == 'POST':
        print("Editing Team")
        team_name = request.form['team_name']
        team_size = request.form['team_size']
        season = request.form['season']

        cursor = db.cursor()
        cursor.execute(
            'UPDATE team'
            ' SET team_name = ?'
            ', team_size = ?'
            ', season = ?'
            ' WHERE id=?', (team_name, team_size, season, id)
        )
        db.commit()
        return redirect(url_for('team.index'))
    elif request.method == 'GET':
        team_details = db.execute(
            'SELECT '
            't.id as team_id'
            ', t.team_name'
            ', t.team_size'
            ', t.season '
            ', tm.id as tm_id'
            ', tm.user_id'
            ', tm.team_id'
            ', tm.submitted_avg'
            ', usr.id'
            ', usr.first_name'
            ', usr.surname '
            'FROM {|schema|}.team AS t'
            ' left join {|schema|}.teamMembers AS tm '
            ' on t.id = tm.team_id'
            ' left join {|schema|}.user AS usr'
            ' on tm.user_id = usr.id'
            ' WHERE t.id =' + str(id)
        ).fetchall()

    return render_template('postal/edit_team.html', team_details=team_details, users=users)

# @bp.route('/del')
# def team_del():
#     db = get_db()
#     db.execute(
#         'DELETE FROM team WHERE id = 1'
#     )
#     db.commit()
#
#     return render_template('postal/manage_team.html')

@bp.route("get_team/<int:id>")
def get_team(id):
    active_comps = query_db(
        'SELECT competition_name FROM {|schema|}.competitions WHERE id IN '
        '(SELECT competition_id FROM {|schema|}.compTeam WHERE team_id=?)', str(id)
    )
    members = get_members(id)

    # if post is None:
    #     abort(404, "Post id {0} doesn't exist.".format(id))
    #
    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    print("Active Comps : ", active_comps)
    print(members)
    return "Done"


@bp.route('/link/<int:team_id>', methods=('GET', 'POST'))
def link_to_comp(team_id):
    if request.method == 'POST':
        print("You have tried to link a competiton")
        comp_id = request.form['linked_comp']
        db = get_db()
        db.execute(
            'INSERT INTO {|schema|}.compTeam (team_id, competition_id) VALUES (%s,%s)', (str(team_id), str(comp_id))
        )
        db.commit()
        return redirect(url_for('team.index'))
    else:
        team = query_db(
                'SELECT id, team_name FROM {|schema|}.team WHERE id=%s', [team_id], one=True
            )
        # print (team)
        comps = query_db(
                'SELECT * FROM {|schema|}.competitions'
            )

    return render_template('postal/link_team.html', competitions=comps, team=team)


@bp.route('/edit/<int:tid>/remove_member/<int:uid>', methods=('GET', 'POST'))
def remove_member(uid, tid):
    db = get_db()
    db.execute(
            'DELETE FROM {|schema|}.teamMembers WHERE user_id=? AND team_id=?', (uid, tid)
        )
    db.commit()
    return redirect(url_for('team.team_edit', id=tid))


@bp.route('/edit/<int:tid>/add_member', methods=('GET', 'POST'))
def add_member(tid):
    uid = request.form['member_selection']
    avg = request.form['sub_avg']
    db = get_db()
    db.execute(
            'INSERT INTO {|schema|}.teamMembers (user_id, team_id, submitted_avg) VALUES(?, ?, ?)', (uid, tid, avg)
        )
    db.commit()
    return redirect(url_for('team.team_edit', id=tid))


@bp.route('/edit/<int:tid>/avg_ud/<int:tm_id>', methods=['GET'])
def member_avg_ud(tid, tm_id):
    avg = request.args.get('avg');
    db = get_db()
    db.execute(
            'UPDATE {|schema|}.teamMembers SET submitted_avg=? WHERE id=?', (avg, tm_id)
        )
    db.commit()
    return '{ status : success}'

@bp.route('/<int:team_id>/stats/<int:comp_id>', methods=['GET'])
def get_team_stats(team_id, comp_id):
    team_results = {
        "graph_data": [],
        "min": 100,
        "max": 0
    }

    members = get_members(team_id)
    for member in members:
        query = """
        SELECT s.result
        FROM {|schema|}.rounds AS r
        JOIN {|schema|}.compTeam AS ct
            ON ct.competition_id = r.comp_id
        JOIN {|schema|}.teamMembers AS tm
            ON tm.team_id = ct.team_id
        LEFT JOIN {|schema|}.scores AS s
            ON s.competition_id = r.comp_id
                AND tm.user_id = s.user_id
                AND r.num = s.round
        JOIN {|schema|}.user AS usr
            ON tm.user_id = usr.id
        WHERE
            r.comp_id=%s
             AND tm.user_id=%s
             AND tm.team_id=%s
        ORDER BY  tm.user_id, r.num asc;
        """

        member_results = {
            'Name': (member['first_name'] + " " + member['surname']),
            'results': [x[0] if x[0] else 0 for x in query_db(query, [comp_id, member['user_id'], team_id])],
            'colour':get_random_colour()
        }
        team_results['graph_data'].append(member_results)

        if len(member_results['results']) > 0 and \
                max(member_results['results']) > team_results['max']:
            team_results['max'] = max(member_results['results'])

        # min_list = filter(lambda a: a != 0, member_results['results'])
        min_list = [x for x in member_results['results'] if x > 0]
        if len(min_list) > 0 and \
                team_results['min'] > min(min_list) :
            team_results['min'] = min(min_list)

    print(json.dumps(team_results))
    return render_template('postal/team_stats.html', graph_data=team_results)


def get_members(team_id):
    query = """SELECT
    tm.*
    , usr.first_name
    , usr.surname
    FROM
        {|schema|}.teamMembers AS tm
    JOIN {|schema|}.user AS usr
        ON tm.user_id = usr.id
    WHERE team_id =%s
    """

    return query_db(query, str(team_id))


def get_random_colour(opacity=0.6):
    from random import randrange
    return "rgba({}, {}, {}, {})".format(randrange(0, 255), randrange(0, 255), randrange(0, 255), opacity)
