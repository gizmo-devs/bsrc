from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, jsonify
)
import datetime
from ..core.db import get_db, query_db
from ..models import team

bp = Blueprint('competition', __name__, )

today = datetime.datetime.today().date()

@bp.route('/')
def index():
    print ('Requesting competition data')
    comp_data = collect_competion_data()
    return render_template('postal/index.html', data=comp_data, date=today)


@bp.route('/competition/create', methods=('GET', 'POST'))
def comp_create():
    if request.method == 'POST':
        print("You have attempted to create a competition")
        competition_name = request.form['competition_name']
        season = request.form['season']

        db = get_db()
        db.execute(
            'INSERT INTO {|schema|}.competitions (competition_name, season) VALUES (?, ?)',
            (competition_name, season)
        )
        db.commit()

        comp_id = query_db('SELECT last_insert_rowid() FROM {|schema|}.competitions', (), one=True)
        return redirect(url_for('competition.comp_edit', comp_id=comp_id[0]))

    return render_template('postal/create_comp.html')


@bp.route('/competition/edit/<int:comp_id>', methods=('GET', 'POST'))
def comp_edit(comp_id=None):
    db = get_db()
    if request.method == 'POST':
        print("You have attempted to Update a competition", comp_id)
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = int(request.form['rounds'])

        due_list = []

        for round in range(rounds):
            r_due = 'round'+ str(round+1) +'_due'
            if request.form.get(r_due) not in ["", "None", None]:
                due_list += [r_due + "='" + request.form.get(r_due) + "'"]
        due =", "
        sql_rounds = due.join(due_list)

        sql_beginning = 'UPDATE {|schema|}.competitions SET competition_name=%s, season=%s,rounds =%s, '
        sql_where = ' WHERE id=?'

        sql = sql_beginning + sql_rounds + sql_where
        print (sql, competition_name, season, rounds, comp_id)
        db.execute(sql, (competition_name, season, rounds, comp_id)
        )
        db.commit()
        return redirect(url_for('competition.index'))

    if request.method == "GET":

        comp_details = query_db(
            'SELECT competitions.*'
            ' FROM {|schema|}.competitions'
            ' WHERE id = %s'
            , [comp_id]
            , one=True
        )

        comp_rounds = query_db("SELECT id, num, due_date FROM {|schema|}.rounds WHERE comp_id=%s", [comp_id])
        return render_template('postal/edit_comp.html', data=comp_details, rounds=comp_rounds)
    return render_template('postal/index.html')


@bp.route('/competition/edit/<int:comp_id>/remove_round/<int:round_id>', methods=('GET', 'POST'))
def remove_round(comp_id, round_id):
    db = get_db()
    db.execute(
            'DELETE FROM {|schema|}.rounds WHERE comp_id=? AND id=?', (comp_id, round_id)
        )
    db.commit()
    return redirect(url_for('competition.comp_edit', comp_id=comp_id))


@bp.route('/competition/edit/<int:comp_id>/add_round', methods=('GET', 'POST'))
def add_round(comp_id):
    round_num = request.form['new_round_num']
    round_due_date = request.form['round_due_date']
    db = get_db()
    db.execute(
            'INSERT INTO {|schema|}.rounds (comp_id, num, due_date) VALUES(?, ?, ?)', (comp_id, round_num, round_due_date)
        )
    db.commit()
    return redirect(url_for('competition.comp_edit', comp_id=comp_id))


@bp.route("/data")
def collect_competion_data():
    competitions = {}
    info = query_db("""
    SELECT
        id
        , competition_name
        , season
        , (
            SELECT COUNT(*)
            FROM {|schema|}.rounds
            WHERE comp_id = competitions.id
            ) as rounds
    FROM {|schema|}.competitions""", []
    )
    comp_list = []
    for comp in info:
        info = dict(
            id=comp['id'],
            name=comp['competition_name'],
            season=comp['season'],
            rounds=comp['rounds']
        )

        comp_dict = {'info':info}

        comp_dict['round_due_dates'] = [round[1] for round in get_comp_due_dates(comp['id'])]
        comp_dict['teams'] = collect_scores(comp['id'])
        comp_list += [comp_dict]
        del comp_dict
    competitions.update({'competitions': comp_list})

    #print(competitions)

    return competitions

@bp.route("/data/compdata")
def collect_competitors_data():
    # competition_id = 1
    data = query_db(
        'SELECT competitions.id'
        ', compTeam.team_id'
        ', teamMembers.user_id'
        ', user.first_name'
        ', user.surname'
        ', scores.round'
        ', scores.estimated'
        ', scores.result'
        ' FROM {|schema|}.competitions'
        ' join {|schema|}.compTeam on competitions.id = compTeam.competition_id'
        ' join {|schema|}.teamMembers on compTeam.team_id = teamMembers.team_id'
        ' join {|schema|}.user on teamMembers.user_id = user.id'
        ' join {|schema|}.scores on teamMembers.user_id = scores.user_id AND compTeam.competition_id = scores.competition_id'
        ' WHERE scores.competition_id=?', [competition_id]
    )

    competitors = {}
    for row in data:
        if row['user_id'] not in competitors:
            competitors[row['user_id']] = {"name":row['first_name'] + " "+ row['surname'] }

    for shooter in competitors:
        print (shooter)
        scores = []
        for row in data:
            if shooter == row['user_id']:
                scores += [{ 'round' : row['round'], 'est' : row['estimated'], 'actual' : row['result']}]
                competitors[shooter].update({"scores" : scores})
    return jsonify(competitors)


@bp.route("/data/user_scores/<comp_id>")
def collect_scores(comp_id):
    # comp_id are params
    #comp_id = 1
    comp_results = []
    for t in get_competition_teams(comp_id):
        # print("Team ID", t)
        current_team = {}
        current_team.update({'team_id': t['team_id'], "u_team_id": t['compteam_id'], "team_name": t['team_name'], "shooters": {}})
        team_results = []
        for team_member in team.get_members(t['team_id']):
            #print(team_member)
            member_results = {}
            member_results['user_id'] = team_member['user_id']
            member_results['name'] = team_member['first_name'] + ' ' + team_member['surname']
            shooter_results = get_compeitors_scores(comp_id, team_member['user_id'], t['team_id'])
            scores = []
            for row in shooter_results:
                scores += [{
                    'score_id' : row['score_id'],
                    'round' : int(row['round'] or 0),
                    'est' : int(row['estimated'] or 0),
                    'actual' : int(row['result'] or 0)
                }]
            member_results['scores'] = scores
            team_results += [member_results]

        current_team["shooters"] = team_results
        comp_results += [current_team]
    return comp_results


@bp.route("/data/comp_teams/<comp_id>")
def get_competition_teams(comp_id):
    teams_in_comp = query_db(
        'SELECT compTeam.id AS compteam_id, team_id, team_name FROM {|schema|}.compTeam '
        ' JOIN {|schema|}.team ON team.id = compTeam.team_id'
        ' WHERE compTeam.competition_id=%s', [comp_id]
    )
    return teams_in_comp


def get_compeitors_scores(comp_id, user_id, team_id):
    user_results = query_db(
        """
        SELECT
-- rounds
rounds.comp_id
, rounds.num
-- compTeam
, compTeam.team_id
, compTeam.competition_id
-- teamMembers
, teamMembers.user_id
-- Scores
, scores.id as score_id
, scores.round
, scores.estimated
, scores.result
, scores.completed
, scores.compTeam_id
FROM {|schema|}.rounds
LEFT JOIN {|schema|}.compTeam
    ON compTeam.competition_id = rounds.comp_id
LEFT JOIN {|schema|}.teamMembers
    ON teamMembers.team_id = compTeam.team_id
LEFT JOIN {|schema|}.scores
    ON scores.competition_id = rounds.comp_id
    AND scores.compTeam_id = compTeam.id
        AND teamMembers.user_id = scores.user_id
        AND rounds.num = scores.round
WHERE
    rounds.comp_id=%s
        AND teamMembers.user_id=%s
        AND teamMembers.team_id=%s;
        """, [comp_id, user_id, team_id]
    )
    return user_results


@bp.route("/<int:comp_id>/due_dates", methods=["GET"])
def get_comp_due_dates(comp_id):
    return query_db(
        "SELECT num, due_date FROM {|schema|}.rounds WHERE comp_id=%s"
        , [str(comp_id)]
    )


@bp.route("/round_result/save", methods=["POST"])
def result_save():
    if request.method == 'POST':
        db = get_db()
        print('You have tried to save a result')
        score_id = request.form['score_id']
        comp_id = request.form['competition_id']
        user_id = request.form['user_id']
        compTeam_id = request.form['compTeam_id']

        est = request.form['estimated']
        res = request.form['actual']
        completed = request.form['date_shot']
        round = request.form['round']
        if request.form['score_id'] in [None, "", 0]:
            sql = "INSERT INTO {|schema|}.scores (user_id, competition_id, completed, estimated, result, round, compTeam_id) VALUES (?,?,?,?,?,?,?)"
            params = (user_id, comp_id, completed, est, res, round, compTeam_id)
        else:
            sql = "UPDATE {|schema|}.scores SET user_id=?, competition_id=?, completed=?, estimated=?, result=?, round=?, compTeam_id=? WHERE id=?"
            params = (user_id, comp_id, completed, est, res, round, compTeam_id, score_id)


        print(sql, params)
        db.execute(sql, params)
        db.commit()
        flash("Record added to the Database")
        return redirect(url_for('competition.index', _anchor=compTeam_id))

@bp.route("/round_result/<int:id>", methods=['GET'])
def result(id=0):
    if request.method == 'GET':
        print(id)
        record_data = query_db(
            'SELECT user_id, competition_id, completed, estimated, result, round, compTeam_id '
            'FROM {|schema|}.scores '
            'WHERE id=%s', [str(id)], one=True
        )
        if record_data is not None:
            print (record_data, type(record_data))
            res_dict = {
                "user_id": record_data['user_id'],
                "competition_id": record_data['competition_id'],
                "completed": record_data['completed'],
                "estimated": record_data['estimated'],
                "result": record_data['result'],
                "round": record_data['round'],
                "compTeam_id" : record_data['compteam_id']
            }
        return jsonify(res_dict)

@bp.route("/competition/due_dates", methods=['GET', 'POST'])
def competition_due_dates():
    comp_details = None
    curr_date = datetime.date.today()
    comps = query_db("SELECT id, competition_name FROM {|schema|}.competitions",[])
    if request.method == "POST":
        comp_id = request.form['comp_sel']
        comp_details = query_db("SELECT num, due_date FROM {|schema|}.rounds WHERE comp_id=%s", [comp_id])

    return render_template('postal/comp_due_dates.html', comp_list=comps, comp_details=comp_details, today=curr_date)
