# Scripts

## sendgrid-clone.py

This script is used to clone the active version of all templates within a given SendGrid account that match an optional prefix and suffix into an existing or new template with a specified suffix

For Example, given my account has the following templates

* MyApp-Registration-Test
* MyApp-Welcome-Test
* MyApp2-Registration-Test
* MyApp-Registration-Prod

If the following command is used
```
sendgrid-clone.py <<SENDGRID API TOKEN HERE>> "-Test" "-Prod" -p "MyApp" 
```

Then the following will occur to the active version of each of our templates:

* MyApp-Registration-Test -> New version added of source template to existing `MyApp-Registration-Prod`
* MyApp-Welcome-Test -> New template created called `MyApp-Welcome-Prod` and a version of the source template is added 
* MyApp2-Registration-Test -> Ignored as it doesn't match our specified prefix
* MyApp-Registration-Prod -> Ignored as it doesn't match our source suffix, but will be altered due to `MyApp-Registration-Test`