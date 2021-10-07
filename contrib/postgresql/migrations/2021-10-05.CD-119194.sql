alter table clients
    add reason_of_decline varchar default NULL;

alter table clients
    add additional_numbers varchar default NULL;

alter table clients
    add additional_emails varchar default NULL;