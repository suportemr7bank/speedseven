"""
Admin site
"""

from django.contrib import admin
import nested_admin

from .models import Profile, ProfileTest, TestScore, Test, TestQuestion, QuestionAlternative, InvestorProfile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Profile admin model
    """

@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    """
    Investor profile admin model
    """


#pylint: disable=no-member
class QuestionAlternativeInline(nested_admin.NestedTabularInline):
    """
    Question alternative inline
    """
    model = QuestionAlternative
    extra = 0


#pylint: disable=no-member
class TestQuestionInline(nested_admin.NestedTabularInline):
    """
    Test question inline
    """
    model = TestQuestion
    inlines = [QuestionAlternativeInline]
    extra = 0


#pylint: disable=no-member
class TestScoreInline(nested_admin.NestedTabularInline):
    """
    Test score inline
    """
    model = TestScore
    extra = 0


#pylint: disable=no-member
class TestInline(nested_admin.NestedTabularInline):
    """
    Test question inline
    """
    model = Test
    inlines = [TestScoreInline, TestQuestionInline]
    extra = 0


#pylint: disable=no-member
class ProfileTestAdmin(nested_admin.NestedModelAdmin):
    """
    Profile test admin model
    """
    list_display = ['id', 'title', 'is_active']
    list_editable = ['is_active']
    inlines = [TestInline]
    change_list_template = 'investorprofile/change_list.html'



admin.site.register(ProfileTest, ProfileTestAdmin)
