from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app as app
)
import pandas as pd

from ..core.auth import login_required
from ..core.db import get_db, query_db

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/")
@login_required
def home():
    edit_button = "<button class='btn btn-info'>Edit</button>"
    df = pd.read_sql_query('SELECT id, first_name, surname, permission_level FROM {|schema|}.user'.replace('{|schema|}', app.config['DB_SCHEMA']), get_db())
    df.columns = ['ID', 'First Name', 'Surname', 'Permission Level']
    df['Edit'] = edit_button
    return render_template('postal/all_users.html',  tables=[df.to_html(classes='table results user', border=0, index=False, index_names=False, escape=False)], titles=df.columns.values)

@bp.route("/<int:user_id>", methods=['GET', 'POST'])
@login_required
def specific_user(user_id):
    if request.method == 'GET':
        sql = 'SELECT * FROM {|schema|}.user WHERE id=%s'
        user = query_db(sql, [user_id], one=True)

        return render_template('postal/user.html', user_data=user)
    elif request.method == 'POST':
        #id = request.form['u_id']
        first_name = request.form['first_name']
        surname = request.form['surname']
        username = request.form['username']
        permission_level = request.form['permission_level']
        sql = 'UPDATE {|schema|}.user SET first_name=%s, surname=%s, username=%s, permission_level=%s WHERE id=%s'
        db = get_db()
        db.cursor().execute(sql, [first_name, surname, username, permission_level, user_id])
        db.commit()
        flash('{} {} has been updated.'.format(first_name, surname))
        return redirect(url_for('user.home'))

@bp.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        #id = request.form['u_id']
        first_name = request.form['first_name']
        surname = request.form['surname']
        username = request.form['username']
        sql = 'INSERT INTO {|schema|}.user (first_name, surname, username) VALUES (%s,%s,%s)'
        db = get_db()
        db.cursor().execute(sql, [first_name, surname, username])
        db.commit()
        flash('{} {} has been created.'.format(first_name, surname))
        return redirect(url_for('user.home'))
    else:
        return render_template('postal/create_user.html', user_data=None)


@bp.route("/<int:user_id>/stats", methods=['GET'])
def user_stats(user_id):
    sel_options = query_db("""SELECT compTeam.competition_id as id
        , competition_name as name
        FROM {|schema|}.teamMembers
            JOIN {|schema|}.compTeam
                ON compTeam.team_id = teamMembers.team_id
            JOIN {|schema|}.competitions
                ON compTeam.competition_id = competitions.id
        WHERE user_id = %s""", [str(user_id)])
    user_details = query_db("SELECT * FROM {|schema|}.user WHERE id = %s", [str(user_id)], one=True)
    fixed_avgs = query_db("""
SELECT
    (SELECT AVG(result) FROM (SELECT result FROM {|schema|}.scores WHERE user_id = %s ORDER BY scores.completed DESC LIMIT 6) as val) AS six_cards,
    (SELECT AVG(result) FROM (SELECT result FROM {|schema|}.scores WHERE user_id = %s ORDER BY scores.completed DESC LIMIT 12) as val) AS twelve_cards,
    (SELECT AVG(result) FROM (SELECT result FROM {|schema|}.scores WHERE user_id = %s AND completed BETWEEN CURRENT_DATE - interval '28 day' AND CURRENT_DATE) as val) as four_weeks,
    (SELECT AVG(result) FROM (SELECT result FROM {|schema|}.scores WHERE user_id = %s AND completed BETWEEN CURRENT_DATE - interval '2 month' AND CURRENT_DATE) as val) as two_months
        """, [user_id, user_id, user_id, user_id], one=True)
    print(fixed_avgs)
    if request.method == 'GET':
        if request.args and request.args.get('comp_id') > '0':
            graph_data = user_comp_stats(user_id=user_id, comp_id=request.args.get('comp_id'))
        else:
            graph_data = previous_round_results(user_id=user_id, rounds=12)

    return render_template('postal/user_stats.html', user=user_details, avgs=fixed_avgs, user_comps=sel_options, graph_data=graph_data)


@bp.route("/<int:user_id>/prev_results/<int:rounds>", methods=['GET', 'POST'])
def previous_round_results(user_id, rounds=12):
    print("user_id", user_id)
    data_set = query_db("""
    SELECT
        result, first_name, surname
    FROM
        {|schema|}.scores
        JOIN {|schema|}.user AS usr ON usr.id = scores.user_id
    WHERE user_id = %s
    --ORDER BY scores.completed DESC
    LIMIT %s
    """, (user_id, rounds))
    results = []
    for val in data_set:
        results += [val['result']]
    data = {
        'comp_id': 0,
        'shooter': data_set[0]['first_name'] + " " + data_set[0]['surname'],
        'rounds': [r for r, idx in enumerate(range(len(data_set)), start=1)],
        'results_arr':results,
        'average' : [(sum(results) / len(results)) for avg in range(len(data_set))]
    }
    return data


@bp.route("/<int:user_id>/stats/<int:comp_id>", methods=['GET', 'POST'])
def user_comp_stats(user_id, comp_id):
    print("user_id", user_id, "comp_id", comp_id)
    data_set = query_db("""
        SELECT
            result, first_name, surname
        FROM
            {|schema|}.scores
            JOIN {|schema|}.user as usr
                ON usr.id = scores.user_id
            WHERE user_id=%s AND competition_id=%s
        order by round
        """, (user_id, comp_id))
    results = []
    for val in data_set:
        results += [val['result']]
    data = {
        'comp_id': comp_id,
        'shooter': data_set[0]['first_name'] + " " + data_set[0]['surname'],
        'rounds': [r for r, idx in enumerate(range(len(data_set)), start=1)],
        'results_arr': results,
        'average': [(sum(results) / len(results)) for avg in range(len(data_set))]
    }
    return data
