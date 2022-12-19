from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SubmitField, IntegerField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Length, Optional


class FilterCell(FlaskForm):
    band = SelectField(     'band',
                            coerce=str,
                            choices=['any'],
                            render_kw={'style': 'width: 20ch'})
    reachable_only = BooleanField('Show only reachable cells')
    submit = SubmitField('Show', render_kw={'style': 'width: 15ch'})

class ScanBandOptions(FlaskForm):
    band = HiddenField(label='')
    start_earfcn =  IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 11ch; height: 3ch'},
                                label='')
    end_earfcn =   IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 11ch; height: 3ch'},
                                label='')
    priority = IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 8ch; height: 3ch'},
                                label='')
    finished = BooleanField(label='')
    save = SubmitField('Save', render_kw={'style': 'width: 15ch'})


class AddJob(FlaskForm):
    band = SelectField(     label='',
                            coerce=str,
                            choices=[],
                            render_kw={'style': 'width: 20ch'})
    start_earfcn =  IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 11ch; height: 3ch'},
                                label='')
    end_earfcn =   IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 11ch; height: 3ch'},
                                label='')
    priority = IntegerField(validators=[Optional(), Length(0, 255)],
                                render_kw={'style': 'width: 8ch; height: 3ch'},
                                label='')


class AutoScan(FlaskForm):
    autoscan = BooleanField(label='')
    save = SubmitField('Save', render_kw={'style': 'width: 15ch'})