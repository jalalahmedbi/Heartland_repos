# Setup Snowflake Oauth on Tableau

show integrations;
show SECURITY INTEGRATIONs;



CREATE or replace SECURITY INTEGRATION TABLEAU_INTDEV_SNOWDEV_HPS_CUTSOM_OAUTH                     
  TYPE = OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = 'https://tableau-dev.heartland.us/auth/add_oauth_token'
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_REFRESH_TOKEN_VALIDITY = 7776000
  BLOCKED_ROLES_LIST = ('ACCOUNTADMIN','SYSADMIN','SECURITYADMIN','USERADMIN')
  ;

desc SECURITY INTEGRATION TABLEAU_INTDEV_SNOWDEV_HPS_CUTSOM_OAUTH;
select system$show_oauth_client_secrets('TABLEAU_INTDEV_SNOWDEV_HPS_CUTSOM_OAUTH');



tsm configuration set -k oauth.snowflake.clients -v " [{\"oauth.snowflake.instance_url\":\"https://wz65202.east-us-2.azure.snowflakecomputing.com\", \"oauth.snowflake.client_id\":\"77DuBRzF32+v6g/UhRdvWd4wRcE=\", \"oauth.snowflake.client_secret\":\"qol3q4/gPmrzh26WU5jG05nOp3gttLOr5TUC5i4m6XI=\", \"oauth.snowflake.redirect_uri\":\"https://tableau-dev.heartland.us/auth/add_oauth_token\" }]"
tsm configuration set -k native_api.enable_snowflake_privatelink_on_server -v true

tsm configuration set -k oauth.snowflake.clients -v " [{\"oauth.snowflake.instance_url\":\"https://wz65202.east-us-2.azure.snowflakecomputing.com\",  \"oauth.snowflake.client_id\":\"77DuBRzF32+v6g/UhRdvWd4wRcE=\",  \"oauth.snowflake.client_secret\":\"qol3q4/gPmrzh26WU5jG05nOp3gttLOr5TUC5i4m6XI=\",  \"oauth.snowflake.redirect_uri\":\"https://tableau-dev.heartland.us/auth/add_oauth_token\" } , {\"oauth.snowflake.instance_url\":\"https://qw29598.east-us-2.azure.snowflakecomputing.com\",  \"oauth.snowflake.client_id\":\"pxjGv0oKyYSaQJaitLbRzn+gyF0=\",  \"oauth.snowflake.client_secret\":\"bZKaf/uTlQ/QG6M9Aq10W/HpZvyC5PNlOBtiiuflsQ0=\",  \"oauth.snowflake.redirect_uri\":\"https://tableau-dev.heartland.us/auth/add_oauth_token\"}]"

[
{\"oauth.snowflake.instance_url\":\"https://wz65202.east-us-2.azure.snowflakecomputing.com\",  
\"oauth.snowflake.client_id\":\"77DuBRzF32+v6g/UhRdvWd4wRcE=\",  
\"oauth.snowflake.client_secret\":\"qol3q4/gPmrzh26WU5jG05nOp3gttLOr5TUC5i4m6XI=\",  
\"oauth.snowflake.redirect_uri\":\"https://tableau-dev.heartland.us/auth/add_oauth_token\" } , 
{
\"oauth.snowflake.instance_url\":\"https://qw29598.east-us-2.azure.snowflakecomputing.com\",  
\"oauth.snowflake.client_id\":\"pxjGv0oKyYSaQJaitLbRzn+gyF0=\",  
\"oauth.snowflake.client_secret\":\"bZKaf/uTlQ/QG6M9Aq10W/HpZvyC5PNlOBtiiuflsQ0=\",  
\"oauth.snowflake.redirect_uri\":\"https://tableau-dev.heartland.us/auth/add_oauth_token\"
}
]"

---------------  Before   ---------------------


[{"oauth.snowflake.instance_url":"https://wz65202.east-us-2.azure.snowflakecomputing.com", "oauth.snowflake.client_id":"77DuBRzF32+v6g/UhRdvWd4wRcE=", "oauth.snowflake.client_secret":"qol3q
4/gPmrzh26WU5jG05nOp3gttLOr5TUC5i4m6XI=", "oauth.snowflake.redirect_uri":"https://tableau-dev.heartland.us/auth/add_oauth_token" }]
 

Old Value:  [{"oauth.snowflake.instance_url":"https://wz65202.east-us-2.azure.snowflakecomputing.com", "oauth.snowflake.client_id":"77DuBRzF32+v6g/UhRdvWd4wRcE
=", "oauth.snowflake.client_secret":"qol3q4/gPmrzh26WU5jG05nOp3gttLOr5TUC5i4m6XI=", "oauth.snowflake.redirect_uri":"https://tableau-dev.heartland.us/auth/add_oauth_token" }]

