import requests
import html
import random
from datetime import datetime


class QuizApp:
    def __init__(self):
        self.api_url = "https://opentdb.com/api.php"
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.user_answers = []
        self.quiz_category = ""
        self.quiz_difficulty = ""
        self.start_time = None
        
    def fetch_questions(self, amount=10, category=None, difficulty=None):
        try:
            params = {'amount': amount, 'type': 'multiple'}
            if category:
                params['category'] = category
            if difficulty:
                params['difficulty'] = difficulty.lower()
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['response_code'] == 0:
                self.questions = data['results']
                self.current_question_index = self.score = 0
                self.user_answers = []
                self.start_time = datetime.now()
                
                for question in self.questions:
                    question['question'] = html.unescape(question['question'])
                    question['correct_answer'] = html.unescape(question['correct_answer'])
                    question['incorrect_answers'] = [html.unescape(ans) for ans in question['incorrect_answers']]
                    all_answers = question['incorrect_answers'] + [question['correct_answer']]
                    random.shuffle(all_answers)
                    question['all_answers'] = all_answers
                return True
            print(f"API Error: Response code {data['response_code']}")
            return False
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return False
    
    def get_current_question(self):
        return self.questions[self.current_question_index] if 0 <= self.current_question_index < len(self.questions) else None
    
    def check_answer(self, user_answer):
        current_q = self.get_current_question()
        if current_q:
            is_correct = user_answer == current_q['correct_answer']
            self.user_answers.append({
                'question': current_q['question'],
                'user_answer': user_answer,
                'correct_answer': current_q['correct_answer'],
                'is_correct': is_correct
            })
            if is_correct:
                self.score += 1
            return is_correct
        return False
    
    def next_question(self):
        self.current_question_index += 1
        return self.current_question_index < len(self.questions)
    
    def get_progress(self):
        return (self.current_question_index + 1, len(self.questions))
    
    def calculate_percentage(self):
        return (self.score / len(self.questions)) * 100 if self.questions else 0.0
    
    def get_quiz_summary(self):
        time_taken = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'category': self.quiz_category,
            'difficulty': self.quiz_difficulty,
            'total_questions': len(self.questions),
            'correct_answers': self.score,
            'incorrect_answers': len(self.questions) - self.score,
            'score_percentage': self.calculate_percentage(),
            'time_taken_seconds': int(time_taken),
            'user_answers': self.user_answers
        }
    
    def reset_quiz(self):
        self.questions = []
        self.current_question_index = self.score = 0
        self.user_answers = []
        self.start_time = None
    
    @staticmethod
    def get_categories():
        return {
            'Any Category': None, 'General Knowledge': 9, 'Books': 10, 'Film': 11, 'Music': 12,
            'Musicals & Theatres': 13, 'Television': 14, 'Video Games': 15, 'Board Games': 16,
            'Science & Nature': 17, 'Computers': 18, 'Mathematics': 19, 'Mythology': 20,
            'Sports': 21, 'Geography': 22, 'History': 23, 'Politics': 24, 'Art': 25,
            'Celebrities': 26, 'Animals': 27, 'Vehicles': 28, 'Comics': 29, 'Gadgets': 30,
            'Anime & Manga': 31, 'Cartoon & Animations': 32
        }
    
    @staticmethod
    def get_difficulties():
        return ['Any Difficulty', 'Easy', 'Medium', 'Hard']