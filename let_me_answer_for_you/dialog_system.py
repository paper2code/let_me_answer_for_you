# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_dialog_system.ipynb (unless otherwise specified).

__all__ = ['DialogSystem']

# Cell
from let_me_answer_for_you import settings
import deeppavlov
import logging
from unittest.mock import patch
from collections import defaultdict

import pandas as pd

logging.basicConfig(
    #filename='example.log',
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.ERROR,
    datefmt='%I:%M:%S'
)

logging.debug(" Debug Log Active")
logging.info("Hello! Welcome to our automated dialog system!")
logging.warning(' Warning Log Active')

# Cell
class DialogSystem:
    ''' The DialogSystem class implements the main methods
    defined in the settings module. \n
    INPUT: \n
    - context_data_file: csv file of contexts (default: None)\n
    - faq_data_file: csv file of FAQs (default: None)\n
    - configs_faq: json config file (default: None)\n
    - download_models: Indicates if download configuration files (default: True)\n

    If the context or the faq files are not provided, a *data* directory with the missing files,
    will be created (in the same path where the module is running). \n
    When an instance is created, the 'run_shell_installs', 'load_and_prepare_data'
    and 'load_qa_models' of the settings module  are called. Also the *data* and *qa_models*
    attributes are created, they store the dataframes and models information, respectively.\n


    If the dataframes are provided they must have the following columns:

     1. context dataframe columns: 'topic', 'context'
     2. faq dataframe columns: 'Question, 'Answer'
    '''
    def __init__(
        self,
        context_data_file=None,
        faq_data_file=None,
        configs_faq=None,
        download_models=True
    ):
        settings.run_shell_installs()
        self.data = {'context': defaultdict(str), 'faq': defaultdict(str)}
        self.download = download_models
        settings.load_and_prepare_data(
            context_data_file=context_data_file,
            faq_data_file=faq_data_file,
            configs_faq=configs_faq,
            data=self.data
        )
        self.qa_models = settings.load_qa_models(
            config_tfidf=self.data['faq']['config'], download=self.download
        )

    def question_answer(self, question):
        ''' Gets answers to a question. \n
        INPUT: \n
        - *question* parameter \n
        The method creates the following attributes:\n
        - 'self.question' -> the input parameter \n
        - 'self.responses' -> a dict of possible responses \n
        - 'self.formatted_responses' -> a formatted string of the possible responses

        This method calls the functions `settings.get_response` and `settings.format_responses`
        '''

        self.question, self.responses = settings.get_responses(
            self.data['context']['df'],
            question,
            self.qa_models,
            nb_squad_results=1
        )
        self.flatten_responses, self.formatted_responses = settings.format_responses(
            self.responses
        )

    def new_question_answer(self, question, answer):
        '''Adds a new question-answer pair.\n
        INPUT:\n
        - question\n
        - answer\n

        The new question-answer pair is stored in the path *self.data['faq']['path']*
        and the models in *qa_models['faq']* get re-trained by calling the function
        `deeppavlaov.train_model`

        '''
        _faq = self.data['faq']
        new_faq = pd.DataFrame({'Question': [question], 'Answer': [answer]})
        _faq['df'] = _faq['df'].append(new_faq)
        _faq['df'].to_csv(_faq['path'], index=False)
        self.qa_models['faq']['tfidf'] = deeppavlov.train_model(
            _faq['config'], download=False
        )
        self.question, self.answer = question, answer
        logging.info('FAQ dataset and model updated..')

    def new_context(self, topic, context):
        ''' Adds a new context. \n
        INPUT:\n
        - topic (The title of the context)
        - context

        The new context is stored in the path *self.data['context']['path']*
        '''
        _ctx = self.data['context']
        new_context = pd.DataFrame({'topic': [topic], 'context': [context]})
        _ctx['df'] = _ctx['df'].append(new_context)
        _ctx['df'].to_csv(_ctx['path'], index=False)
        self.topic, self.context = topic, context
        logging.info('contexts dataset updated..')