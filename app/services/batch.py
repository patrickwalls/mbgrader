from typing import Callable, Any
import numpy as np
from app import app, db
from ..models import Batch, Response, BatchResponse


class BatchService:
    def __init__(
        self,
        *,
        batch_id: int = None,
        grade: int = None,
        comments: str = None,
        datatype_id: int = None,
        next_id: int = None,
        previous_id: int = None,
        question_id: int = None,
    ):
        self.grade = grade
        self.comments = comments
        self.datatype_id = datatype_id
        self.next_id = next_id
        self.previous_id = previous_id
        self.question_id = question_id
        self.id = batch_id

    def create(self) -> dict:
        new_batch = Batch(
            grade=self.grade,
            comments=self.comments,
            datatype_id=self.datatype_id,
            question_id=self.question_id,
            next_id=self.question_id,
            previous_id=self.previous_id,
        )
        db.session.add(new_batch)
        db.session.commit()
        self.id = new_batch.id
        return new_batch.to_dict()

    def compare(
        self,
        response: Response,
        preprocessing: Callable[[int, str], Any] = None
    ) -> bool:
        model = Batch.query.get(self.id)
        if model.datatyoe.id != response.datatype.id:
            return False

        response_data = response.get_data()
        batch_data = model.get_data()
        if preprocessing:
            try:
                response_data = preprocessing(
                    response.student_id, response_data
                )
                batch_data = preprocessing(
                    model.batch_response[0].response.student_id,
                    batch_data,
                )
            except Exception as e:
                print(f"Preprocessing failed: {e}")
        
        dtype = model.datatype.name
        if dtype in ["text", "symbolic", "logical"]:
            return batch_data == response_data

        elif dtype == "numeric":
            return (
                np.array_equal(batch_data.shape, response_data.shape)
                and np.allclose(batch_data, response_data, atol=model.question.tolerance)
            )
        elif dtype == 'figure':
            diffs = np.zeros([len(batch_data),len(response_data)])
            for sss in range(0, len(batch_data)):
                for aaa in range(0, len(response_data)):
                    if response_data[aaa].size > 2 and batch_data[sss].size > 2:
                        x_response = response_data[aaa][:,0]
                        y_response = response_data[aaa][:,1]
                        x_batch = batch_data[sss][:,0]
                        y_batch = batch_data[sss][:,1]
                        L_response = np.sum(np.sqrt(np.diff(x_response)**2 + np.diff(y_response)**2))
                        L_batch = np.sum(np.sqrt(np.diff(x_batch)**2 + np.diff(y_batch)**2))
                        #if np.abs(L_response - L_batch)/L_batch > 0.01:
                        #    diffs[sss,aaa] = 999
                        #    continue
                        t_response = np.concatenate([[0],np.cumsum(np.sqrt(np.diff(x_response)**2 + np.diff(y_response)**2))])
                        t_batch = np.concatenate([[0],np.cumsum(np.sqrt(np.diff(x_batch)**2 + np.diff(y_batch)**2))])
                        x_interp = np.interp(t_response, t_batch, x_batch)
                        x_diff = np.max(np.abs(x_interp - x_response))
                        y_interp = np.interp(t_response, t_batch, y_batch)
                        y_diff = np.max(np.abs(y_interp - y_response))
                        diffs[sss,aaa] = np.max([x_diff,y_diff])
                    elif response_data[aaa].size == 2 and batch_data[sss].size == 2:
                        diffs[sss,aaa] = np.max(np.abs(response_data[aaa] - batch_data[sss]))
                    else:
                        diffs[sss,aaa] = 999
            diffs = diffs < model.question.tolerance
            if np.all(diffs.sum(axis=0)) and np.all(diffs.sum(axis=1)):
                return True
            else:
                return False
        else:
            return False

    def grade(self) -> dict:
        model = Batch.query.get_or_404(self.id)
        model.grade = self.grade
        model.comments = self.comments
        db.session.add(batch)
        db.session.commit()
        return model.to_dict()
