# Email templates usage


1. Create a override folder inside template folder

2. Remove override folder from repository to avoid conflict (add it in .gitignore)
    
    Templates are created and saved inside this folder, if its content changes in the server folder, there will be conflict when trying to make a pull in the server.

3. Add template path to settings:

        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    ...
                    os.path.join(BASE_DIR, 'emailtemplates', 'templates/override/')],
                'APP_DIRS': True,
                ...
            },
        ]

4. Put email template folder and files inside override folder

    Follow template folder structure.
    
    Exemple:
        invitations/email/email_templates.*

    This template will have preference in django template searching


5. You may use view to create email templates. It will be saved in the
overide folder, according to prefix. This mode allows email template edition by the user.

    Example:
    
    If prefix is invitations/email/email_invite, and all fields are typed, 3 files will be cerated:
    
    1. email_invite_message.html
    2. email_invite_message.txt
    1. email_invite_subject.txt

