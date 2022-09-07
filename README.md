# Media Manager for Music 
My own web-based media manager for music. 

# Instructions
Before downloading the code. You should have a working developer build on spotify https://developer.spotify.com/dashboard/login. <br>
Upon login, create a new app and obtain the Cliend ID, and Secret Key <Beware! Do not share this with anyone>. <br>
On the top right, "Edit Settings" and under the "Redirect URIs" section, add the following uri's.

```
- http://localhost5000/redirect 
- http://localhost5000/redirect/
- http://127.0.0.1:5000/redirect
- http://127.0.0.1:5000/redirect/ 
```

After the sucess from above. 
```
$ git clone
$ cd into the project
$ cd `credentials` and add your `Cliend ID` and Secret Key
$ 
```
