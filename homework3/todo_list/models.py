from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.Integer, default=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return (
            f'<Task(id={self.id}, done={self.done}, description="{self.description}")>'
        )
