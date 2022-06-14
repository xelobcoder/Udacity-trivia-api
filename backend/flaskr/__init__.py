import os
from unicodedata import category
from flask import Flask, after_this_request, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app,resources={r"/": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        # query the db for all categories
        categories = Category.query.all()
        # create a list of category objects
        allCategories = [category.format() for category in categories]
        # return the list of category objects
        return jsonify({
            'success': True,
            'categories': allCategories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        # query the db for all questions
        questions = Question.query.all()
        # create a list of question objects
        allQuestions = [question.format() for question in questions]
        #handle category list format 
        categories  = [category.format() for category in Category.query.all()]
        # return the list of question objects

        return jsonify({
            'success': True,
            'questions': allQuestions,
            'total_questions': len(allQuestions),
            'current_category': None,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # query the db for the question
        question = Question.query.filter(Question.id == question_id).one_or_none()
        # if the question is not found, return an error
        if question is None:
            abort(404)
        # delete the question
        question.delete()
        # return a success message
        return jsonify({
            'success': True,
            'deleted': question_id
        })

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        # get the data from the request
        body = request.get_json()
        # if the data is not valid, return an error
        if not ('question' in body and 'answer' in body and 'category' in body and 'difficulty' in body):
            abort(422)
        # create a new question object
        question = Question(
            question= body['question'],
            answer=body['answer'],
            category=body['category'],
            difficulty=body['difficulty']
        )
        # add the question to the database
        question.insert()
        # return a success message
        return jsonify({
            'success': True,
            'created': question.id
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # get the data from the request
        body = request.get_json()
        # if the data is not valid, return an error
        if not ('searchTerm' in body):
            abort(422)
        # query the db for all questions that match the search term
        questions = Question.query.filter(Question.question.ilike('%' + body['searchTerm'] + '%')).all()
        # create a list of question objects
        allQuestions = [question.format() for question in questions]
        # return the list of question objects
        return jsonify({
            'success': True,
            'questions': allQuestions,
            'total_questions': len(allQuestions)
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        # check if the category exists
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
            abort(404)    
        # query the db for all questions that match the category_id
        questions = Question.query.filter(Question.category == category_id).all()
        # create a list of question objects
        allQuestions = [question.format() for question in questions]
        # return the list of question objects
        return jsonify({
            'success': True,
            'questions': allQuestions,
            'total_questions': len(allQuestions)
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        # get the data from the request
        body = request.get_json()
        # if the data is not valid, return an error
        if not ('quizCategory' in body and 'previousQuestions' in body):
            abort(422)  
        # get the category id
        category_id = body['quizCategory']
        # get the previous questions
        previous_questions = body['previousQuestions']

        # get all questions from the category

        questions = Question.query.filter(Question.category == category_id).all()

        # create a list of question objects
        allQuestions = [question.format() for question in questions]

        # create a list of question ids
        all_question_ids = [question['id'] for question in allQuestions]

        # create a list of previous question ids
        previous_question_ids = [question['id'] for question in previous_questions]

        # create a list of question ids that are not in the previous questions
        new_question_ids = [question_id for question_id in all_question_ids if question_id not in previous_question_ids]

        # get a random question id from the list of new question ids
        random_question_id = random.choice(new_question_ids)

        # get the question object from the random question id
        random_question = Question.query.filter(Question.id == random_question_id).one_or_none()

        # if the question is not found, return an error
        if random_question is None:
            abort(404)

        # return the question object
        return jsonify({
            'success': True,
            'question': random_question.format()
        })
        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

