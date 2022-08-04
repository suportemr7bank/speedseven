"""
Products agreement renderers
"""

from django.template import Context, Template


class BaseRenderer:
    """
    Base class form agreement template rendering
    """

    @classmethod
    def render(cls, user, agreement_text, extra_args=None, preview=False) -> str:
        """
        Render the client agreement according to agreement
        """
        if preview:
            data = cls.preview_data()
        else:
            data = cls.content_data(user, extra_args)

        template = Template(agreement_text)
        context = Context(data)
        text = template.render(context)

        # Using buitin template tags break lines
        template = Template("{{ text|safe }}")
        context = Context({'text': text})

        return template.render(context)

    @classmethod
    def content_data(cls, user, extra_args=None):
        """
        Data to be rendered related to the available tags
        """
        return dict()

    @classmethod
    def preview_data(cls):
        """
        Fake bata to be rendered as preview
        """
        return dict()

    @classmethod
    def available_tags(cls):
        """
        Available tags
        """
        return []


class DefaultAgreementRender(BaseRenderer):
    """
    Agreement rendering according to a template
    """

    @classmethod
    def content_data(cls, user, extra_args=None):
        """
        Data to be rendered related to the available tags
        """
        return {
            'name': user.get_full_name(),
            'email': user.email
        }

    @classmethod
    def preview_data(cls):
        """
        Data to be rendered related to the available tags
        """
        return {
            'name': 'User Fake Name',
            'email': 'fakemail@server.com'
        }

    @classmethod
    def available_tags(cls):
        """
        Available tags
        """
        return ['name', 'email']
