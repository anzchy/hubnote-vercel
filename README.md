# HubNote-Vercel

一个简洁的 GitHub Issues 管理工具，帮助你更好地跟踪和管理多个仓库的 Issues。

这是云端操作的版本，目前部署在 Vercel app.

Totally Free of charge.

## How to use this repo：

1.You need to have an github account, if you don't have, create one,  then you can write an email to me: anzchy@163.com,  I will add your account name in whitelist, currently no fees.

2.Log in to your github account, create a repo, for example `hubnote-test`, then in `hubnote-test` repo, create several `issues`, 

![image-20250816110814894](../../../Library/Application Support/typora-user-images/image-20250816110814894.png)

![image-20250816110944227](../../../Library/Application Support/typora-user-images/image-20250816110944227.png)

you can see issues as a folder in your Evernote app, and in each issue, we can add hundreds of comments, you can see every commet  as an seperate article.

| Github Repo | Evernote and other note-taking app                           |
| ----------- | ------------------------------------------------------------ |
| Issues      | Folders, subjects can be like `projects`, or `study`, `life` , `finance`, etc. |
| coments     | Articles                                                     |

3. in your repo, you need to generate an access token of your repo, just for this repo, this token is for the hubnote website to interact with your specific repo (`hubnote-test`  in my example.)

(1) go to setting in your account, not setting in your repo

![image-20250816111043267](../../../Library/Application Support/typora-user-images/image-20250816111043267.png)

（2）scroll down, and in the left panel, click in `Developer setting` button.

in `Developer Settings -> Personal access tokens -> Tokens(classic) -> Generate new token`, then click `Generate new token(Fine-grained, repo-scope)`.

![image-20250816111402021](../../../Library/Application Support/typora-user-images/image-20250816111402021.png)

(3) Set the token environment

Name: you can create any name you like, in my example, just name it as `hubnote`, 

Expiration: Better set this as No expiration, it's up to you.

Repository access:  click `Only select repositories`, then select your repo ,in my case, `hubnote-test` repo.

Permissions: Click on `Add permissions`, then add `Issues`,  Access should be `Read and write`.

![image-20250816111805467](../../../Library/Application Support/typora-user-images/image-20250816111805467.png)

After having finished all of the above setting, Click `Generate token` below, 

![image-20250816112322375](../../../Library/Application Support/typora-user-images/image-20250816112322375.png)

then you will get a series of seemingly random characters like this. cope and save it in your local text file.

`github_pat_11B*******` 

this token will serve as your login password in hubnote website.



4. Visit [hubnote website](https://hubnote.jackcheng.tech)，in the `用户名(name)` input box, fill in your github account name, in the `密码(password)` input box, paste in your token. then Click `登录`, Finally you are in, 

5. Congratulations, Welcome to the HubNote World.

   ![image-20250816112741553](../../../Library/Application Support/typora-user-images/image-20250816112741553.png)
