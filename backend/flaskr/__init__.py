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
    CORS(app, resources={'/': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        # query the db for all categories
        categories = Category.query.all()
        # create a dictionary of categories
        allCategories = {}
        for category in categories:
            allCategories[category.id] = category.type

        # return the list of category objects
        return jsonify({
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
        categories  =  {category.id: category.type for category in Category.query.all()}
        # get the page number
        page = request.args.get('page', 1, type=int)
        # get the questions for the current page
        questions = allQuestions[(page-1)*QUESTIONS_PER_PAGE:page*QUESTIONS_PER_PAGE]
         # get the total number of questions
        total_questions = len(questions)
        # return the list of question objects
        print(categories)
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': total_questions,
            'categories': categories,
            'current_category': None
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
        print('inserted')
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
            'total_questions': len(allQuestions),
            'current_category': None,
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
            'questions': allQuestions,
            'total_questions': len(allQuestions),
            'currentCategory': Category.query.filter(Category.id == category_id).one_or_none().type
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
    def play_quiz_questions():
        # get the data from the request
        body = request.get_json()
        print(body)
        # if the data is not valid, return an error
        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422)  
        # get the category id
        category_id = body['quiz_category'] 
        # get the category type from category_id dictionary
        category_type = category_id['type']
        # get category id from the category_id dictionary
        categoryid = category_id['id']
        # get the previous questions
        previous_questions = body['previous_questions']
        # get last previous question

        last_question = None
        if len(previous_questions) > 0:
            last_question = previous_questions[-1]
        # query the db for all questions that match the category_id
        
        category_questions = None
        quiz_category = None
        if category_type == 'click' and categoryid == 0:
            category_questions = Question.query.all()
            quiz_category = 'All'
        else:
            category_questions = Question.query.filter(Question.category == categoryid).all()
            quiz_category = Category.query.filter(Category.id == categoryid).one_or_none()
        # get random question from the category_questions
        random_question = None
        if len(category_questions) > 0:
            random_question = category_questions[random.randint(0, len(category_questions) - 1)]
        
        if random_question is not None and random_question.id not in previous_questions:
            question = random_question.format()
            return jsonify({
                'success': True,
                'question': question
            })
        elif random_question is not None and random_question.id in previous_questions:
            if len(previous_questions) == len(category_questions):
                return jsonify({
                    'success': False,
                    'question': None
                })
            else:
                return play_quiz_questions()
  
       

        

     
               
        
        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.

    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500
    return app

