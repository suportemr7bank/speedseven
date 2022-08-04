"""
Investor profile models
"""

import json
from django.conf import settings
from django.db import models
from tinymce import models as tinymce_models

class Profile(models.Model):
    """
    Investor profile
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Perfil de investidor'
        verbose_name_plural = 'Perfís de investidor'

    name = models.CharField(max_length=128, verbose_name='Nome descritivo', unique=True)
    display_text = models.CharField(
        max_length=128, verbose_name="Texto de exibição")

    # pylint: disable=invalid-str-returned
    def __str__(self) -> str:
        return self.display_text


class ProfileTest(models.Model):
    """
    Profile test
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Teste de perfil de investidor'
        verbose_name_plural = 'Testes de perfís de investidor'

    title = models.CharField(max_length=256, verbose_name='Título')
    description = models.TextField(
        verbose_name='Descrição', null=True, blank=True)
    info = models.TextField(
        verbose_name="Informações para o usuário", null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=False)
    published = models.BooleanField(verbose_name='Publicado', default=False)

    # pylint: disable=invalid-str-returned
    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        # Must have only one active
        # In case more than one is set active, the last saved will be the active
        # pylint: disable=no-member
        ProfileTest.objects.filter(is_active=True).update(is_active=False)
        return super().save(*args, **kwargs)

class Test(models.Model):
    """
    Group questions in investor profile test
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Teste'
        verbose_name_plural = 'Testes'

    profile_test = models.ForeignKey(
        ProfileTest, verbose_name='Teste do perfil', on_delete=models.CASCADE)
    title = models.CharField(max_length=512, verbose_name='Texto do teste')

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.profile_test.title} - {self.title}'


class TestScore(models.Model):
    """
    Profile score
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Pontuação do teste'
        verbose_name_plural = 'Pontuação dos testes'
        constraints = [
            models.UniqueConstraint(
                fields=['test', 'profile'], name='unique_test_score')
        ]

    test = models.ForeignKey(
        Test, verbose_name='Teste', on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, verbose_name='Perfil', on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name='Pontução do perfil')

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.test.title} - {self.profile.display_text} - {self.score}'


class TestQuestion(models.Model):
    """
    Profile test question
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Questão do teste'
        verbose_name_plural = 'Questões dos testes'

    test = models.ForeignKey(
        Test, verbose_name='Teste do perfil', on_delete=models.CASCADE)
    text = tinymce_models.HTMLField(verbose_name='Texto da questão')

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.test.title} - {self.text}'


class QuestionAlternative(models.Model):
    """
    Question alternatives
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Alternativa da questão'
        verbose_name_plural = 'Alternativas das questões'

    test_question = models.ForeignKey(
        TestQuestion, verbose_name='Questão do teste', on_delete=models.CASCADE)
    text = models.CharField(
        max_length=512, verbose_name='Texto da alternativa')
    score = models.IntegerField(verbose_name='Pontuação da alternativa')

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.test_question.test.title} - {self.text} - {self.score}'


class InvestorProfile(models.Model):
    """
    User profile test
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Perfil de investimento do usuário'
        verbose_name_plural = 'Perfis de investimento dos usuários'

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name='investidor', on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, verbose_name='Perfil do investidor', on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True)
    profile_test = models.ForeignKey(
        ProfileTest, verbose_name='Teste aplicado', on_delete=models.CASCADE)
    test_data = models.TextField(verbose_name='Resultado do teste')

    def get_test_answers(self) -> dict:
        """
        Performed test answers
        In case the test is updated, the answares are keep
        """
        return json.loads(self.test_data)

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.user.email} - {self.profile.display_text} - {self.profile_test.title} ({self.profile_test.pk})'
