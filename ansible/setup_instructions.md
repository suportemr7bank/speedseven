# Initial requirements

## 1. install SSH key authentication in the server

    Creating ssh key (Ubuntu 20.04):

        In the client machine (your machine)
        
            cd to ~/.ssh

            Generantin key:
                
                ssh-keygen -b 4096
                choose file name
                press Enter...

            Copy to server (remote):

                ssh-copy-id -i <file_name>.pub <user>@<hots_ip>

            Test login:

                ssh <user>@<hots_ip>

## 2. Run playbook (step 1)

    cd to ../ansible folder (local machine)

    run:

        ansible-playbook server_setup/server_setup.yaml --tag "user" -i hosts.yaml --limit <host>,

    test:
        
        To switch to speedseven user type the command: 
        
            su - speedseven

## 3. Configure git repository access key
    
    cd to (server): 
    
        /webapps/.ssl

        cat /webapps/.ssl/<host>.pub

        copy the output to the repository key access configuration (Follow repository instructions)
        

## Run playbook (step 2)

    run:

        ansible-playbook server_setup/server_setup.yaml -i hosts.yaml --limit <host>,