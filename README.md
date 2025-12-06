1. App Name: StuddyBuddy

2. App Tagline: Find your perfect study buddies at Cornell.

3. Link to GitHub repo: https://github.com/Oliviayuuuu317/hack-challenge.git

4. Some screenshots of your app (highlight important features)

5. Users sign in with their Google account, then add Cornell courses and sessions to their profile to build their course schedule. They can search based on course and session preferences, and the app will recommend the top 10 users who share the same courses, sessions, or optional interests.

6.
Backend:

[Login Authentication]
 Routes: POST(Google OAuth login)
 Google login auto creates a User row in the USER TABLE

[User Profiles]
 Routes: GET(user) & POST(update user) & DELETE(user)
 USER table connects to SESSION TABLE, FRIEND TABLE, MESSAGE TABLE, MAJOR TABLE, INTEREST TABLE through relationships
 (INTERESTCATEGORY TABLE and INTEREST TABLE is one-to-many relationship)

[Friendships]
 Routes: GET(friends) & POST(friend request/accept or deny) & DELETE(fiend)
 USER TABLE and FRIEND TABLE is one-to-many relationship (friends reference two users). 

[Courses and Sessions]
 Routes: GET(all courses/course with all sessions) & DELETE(course/session)
 COURSE TABLE and SESSION TABLE is one-to-many relationship, SESSION TABLE and USER TABLE is   
 many-to-many relationships.

[Schedule]
Routes: GET(user's schedule) & POST(add session to schedule) & DELETE(session from schedule)

[Messaging System] (only has code in backend)
 Routes: POST(send message) & GET(conversation history/inbox preview) & DELETE(message)
 USER TABLE and MESSAGE TABLE is one-to-many relationship

[Matching and Recommendations]
 Routes: GET(relevant courses/sessions) & POST(suggests top 10 study buddies)
 Matching logic evaluates shared sessions, majors, interests


7. Anything else you want your grader to know

Note: The link, screenshots, and description will be used for the Hack Challenge website where we will showcase everyone’s final projects
