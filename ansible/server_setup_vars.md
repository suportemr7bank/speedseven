# Adding new host to inventory:

  1. Create a ansible/hosts_vars/ if it does not exist
    
  2. Copy file ansible/server_vars.example.yaml folder into the folder created
    
  3. Edit this file and set variable values
    
  4. Rename file:
        Ex: server_vars.example.yaml => <server_name_new>.yaml
    
  5. Edit hosts.yaml (or create it) in ansible root to insert the new host

  ## Example (hosts.yaml):

    all:
    children:
      webservers:
        hosts:
          server_name:
            ansible_host: server_name.com
            
          <server_name_new>:
            ansible_host: <server_name_new>.com
            ...

          ...

        vars:
          ansible_ssh_user: root
          ssl_target_folder: /etc/ssl
