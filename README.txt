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
COURSE TABLE and SESSION TABLE is one-to-many relationship, SESSION TABLE and USER TABLE is many-to-many relationships.

[Schedule]
Routes: GET(user's schedule) & POST(add session to schedule) & DELETE(session from schedule)

[Messaging System] (only has code in backend)
Routes: POST(send message) & GET(conversation history/inbox preview) & DELETE(message)
USER TABLE and MESSAGE TABLE is one-to-many relationship

[Matching and Recommendations]
Routes: GET(relevant courses/sessions) & POST(suggests top 10 study buddies)
Matching logic evaluates shared sessions, majors, interests

Frontend:
1. Login Page Using Google
The app begins with a welcome/sign-in screen that prompts the user to sign in using Google. There's a “Continue with Google” button that triggers Google OAuth. Once tapped, the user is redirected to the Google account selection screen, where users can select an existing account already logged in on the device, or users may enter their email and password through the standard Google login pages. After successful authentication, the app returns the user to a personalized welcome screen (e.g., Welcome, John).

2. Setting Up Personal Information (Profile Creation Flow)
After logging in for the first time, the user is guided through a multi-step profile setup. 
(1st screen) Basic Info that asks for First name, Last name, Pronouns. Once these fields are validated, and users can proceed using the Next button.
(2nd screen) Contact Info that asks for Email (auto-filled from Google login but still shown), Phone number
(3rd screen) A profile photo screen that allows users to upload a profile picture from their device, or skip the step.
(Final profile preview screen) shows Profile photo, Name, Pronouns, Email, Phone number and they confirm by clicking Done.

3. Choosing Courses From Cornell's Course Roster
The home page displays the user's profile and an empty schedule. When users tap Add classes, they are brought to a course search interface. Users can search by subject or course number. Then they can view matching courses from Cornell’s course roster, with Course number and section (e.g., Chem 2070-001) and tap the course’s plus button to add it to their schedule.

4. Editing Their Schedule (Adding & Deleting Courses)
After selecting courses, the home schedule view updates to show the added classes as large cards. Users can manage their schedule by adding more courses, removing courses, and the app displays the updated schedule immediately.

5. Add Study Buddies
Users can open the side menu and search a course, it will show people who are also in the course, and the user can request to add them as a friend. Besides sending requests to other users, users can also view incoming friend requests and accept/reject them. Users can view current connections(friend list) and remove friends if they want. 

Design:



7. 

Note: The link, screenshots, and description will be used for the Hack Challenge website where we will showcase everyone’s final projects
