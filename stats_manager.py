import os
import json
import pandas as pd
import numpy as np

class StatsManager:
    def __init__(self, root):
        self.root = root
        self.csv_file = "data/quiz_history.csv"
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.csv_file):
            pd.DataFrame(columns=['date', 'category', 'difficulty', 'total_questions', 'correct_answers',
                                 'incorrect_answers', 'score_percentage', 'time_taken_seconds', 'user_answers']).to_csv(self.csv_file, index=False)
    
    def _read_df(self):
        try:
            df = pd.read_csv(self.csv_file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    
    def save_quiz_result(self, summary):
        summary['user_answers'] = json.dumps(summary['user_answers'])
        df = self._read_df()
        df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
        df.to_csv(self.csv_file, index=False)
    
    def get_total_quizzes(self):
        return len(self._read_df())
    
    def get_recent_quizzes(self, n):
        df = self._read_df()
        return df.tail(n).sort_values('date', ascending=False) if len(df) > 0 else pd.DataFrame()
    
    def get_statistics_summary(self):
        df = self._read_df()
        if len(df) == 0:
            return {'total_quizzes': 0, 'total_questions_answered': 0, 'mean_score': 0, 'median_score': 0,
                   'mode_score': 0, 'std_deviation': 0, 'overall_accuracy': 0, 'best_score': 0, 'worst_score': 0}
        scores = df['score_percentage'].values
        mode_vals = pd.Series(scores).mode()
        return {
            'total_quizzes': len(df),
            'total_questions_answered': df['total_questions'].sum(),
            'mean_score': round(scores.mean(), 1),
            'median_score': round(np.median(scores), 1),
            'mode_score': round(float(mode_vals.iloc[0]) if len(mode_vals) > 0 else scores.mean(), 1),
            'std_deviation': round(scores.std(), 2),
            'overall_accuracy': round((df['correct_answers'].sum() / df['total_questions'].sum() * 100) if df['total_questions'].sum() > 0 else 0, 1),
            'best_score': round(scores.max(), 1),
            'worst_score': round(scores.min(), 1)
        }