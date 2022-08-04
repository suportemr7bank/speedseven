"""
Investor provile forms
"""


import json
from django import forms
from django.db.models import F, Sum
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Row, Field


from . import models


def create_form_class(profile_test_obj):
    """
    Create form class based on model object
    """

    class ProfileTestForm(forms.Form):
        """
        Profile test dynamic form
        """

        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)
            self.instance = kwargs.pop('instance', None)
            super().__init__(*args, **kwargs)

            if self.instance and self.instance.profile_test.published:
                for _key, field in self.fields.items():
                    field.disabled = True

            if self.instance:
                self.initial = json.loads(self.instance.test_data)
                self._profile_test_obj = self.instance.profile_test
            else:
                self._profile_test_obj = profile_test_obj

            test_title = self._build_form()

            self.helper = FormHelper()
            # for position in title_position:
            fields = list(self.fields.keys())
            for title in test_title:
                fields.insert(
                    title['position'],
                    HTML(f'<h3 class="pb-2 pt-4">{title["title"]}</h3>')
                )
            fields.insert(
                0, HTML(f'<p class="pb-2 h2">{self._profile_test_obj.title}</p>'))
            fields.insert(
                1, HTML(f'<p class="p-2 mb-2">{self._profile_test_obj.info}</p>'))

            self.helper.layout = Layout(*fields)

        def _build_form(self):
            # Test profile is a group of tests which is a group of questions
            test_title = []
            count = 0
            if self._profile_test_obj:
                test_set = getattr(self._profile_test_obj, 'test_set', None)
                for test in test_set.all().order_by('pk'):
                    if test:
                        test_title.append(
                            {'title': test.title, 'position': count})
                        count += 1

                        questions = test.testquestion_set.all().order_by('pk')
                        for question in questions:
                            alternatives = question.questionalternative_set.all().order_by('pk')
                            choices = []
                            for alternative in alternatives.values_list('pk', 'text'):
                                choices.append((alternative))

                            has_choices = len(choices) > 0
                            field_name = f'question_{question.pk}'
                            self.fields[field_name] = forms.ChoiceField(
                                label=mark_safe(question.text),
                                choices=choices,
                                widget=forms.RadioSelect(),
                                required=has_choices,
                                disabled=(not has_choices)
                            )
                            count += 1
            return test_title

        def save(self, commit=True):
            """
            Create the investor profile
            """

            questions_ids = [ q_id for q_id in self.cleaned_data.values() if q_id != '' ]

            user_test_data = json.dumps(self.cleaned_data)

            profile = self._eval_profile(questions_ids)

            obj = None
            if commit:
                #pylint: disable=no-member
                obj = models.InvestorProfile.objects.create(
                    user=self.user,
                    profile_id=profile,
                    profile_test=self._profile_test_obj,
                    test_data=user_test_data
                )
            return obj

        def _eval_profile(self, questions_ids):
            scores = self._extract_data(
                self._get_test_scores(questions_ids), 'pk')

            profiles = []
            for _test, score in scores.items():
                for i in range(0, len(score)-1):
                    scr = score[i]['score']
                    if score[i]['test_score'] <= scr < score[i+1]['test_score']:
                        profiles.append(score[i]['test_profile'])

                i += 1
                scr = score[i]['score']
                if score[i]['test_score'] <= scr:
                    profiles.append(score[i]['test_profile'])

            profile = min(profiles)
            return profile

        def _get_test_scores(self, questions_ids):
            scores = self._profile_test_obj.test_set.filter(
                testquestion__questionalternative__in=questions_ids
            ).values(
                'pk'
            ).annotate(
                test_score=F('testscore__score'),
                test_profile=F('testscore__profile'),
                score=Sum('testquestion__questionalternative__score'),
            ).order_by('pk', 'test_score')
            return scores

        def _get_test(self, questions_ids=None):
            if questions_ids:
                test = self._profile_test_obj.test_set.filter(
                    testquestion__questionalternative__in=questions_ids)
            else:
                test = self._profile_test_obj.test_set.all()

            test = test.annotate(
                test_question=F('testquestion__text'),
                alternative=F('testquestion__questionalternative__text'),
                score=F('testquestion__questionalternative__score')
            ).order_by('pk').values('title', 'test_question', 'alternative', 'score')
            return test

        def _extract_data(self, questions, field):
            questions_data = dict()
            for item in list(questions):
                questions_data.setdefault(item[field], []).append(
                    self._pop(item, field))

            return questions_data

        def _pop(self, _dict, key):
            _dict.pop(key)
            return _dict

    return ProfileTestForm


class ProfileForm(forms.ModelForm):
    """
    Profile test dynamic form
    """

    class Meta:
        """
        Meta class
        """
        model = models.ProfileTest
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['published'].label = 'Publicar teste'
        self.fields['description'].widget.attrs['rows'] = 4
        self.fields['info'].widget.attrs['rows'] = 7

        if self.instance.pk and self.instance.published:
            for _key, field in self.fields.items():
                field.disabled = True

        self.fields['is_active'].disabled = False

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row('title'),
            Row(Field('description', attrs={'rows': 5})),
            Row('info'),
            Row('is_active'),
            Row(HTML(
                '<hr>'
                '<div class="text-success">Atenção! Testes publicados não podem ser editados</div>'
                '<small class="text-secondary mb-3">(A modificação do teste invalida as respostas dadas pelo cliente)</small>'
            )),
            Row('published'),
        )
