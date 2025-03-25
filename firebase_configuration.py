import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt


# Path to your Firebase service account key
# This credential is used to authenticate your app with Firebase and allows it to securely interact with Firebase services (such as Firestore, Authentication, etc.).
cred = credentials.Certificate("private_key_of_database.json")



# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Reference to the users collection
users_ref = db.collection('users')

# Login with username and password function
def user_exist(username, password):
    try:
        # Query to find the user document where 'username' is equal to the provided username
        query = users_ref.where(filter=('username', '==', username)).limit(1).stream()


        # Check if user exists
        for user_doc in query:
            # Check if the password matches the one stored in Firestore
            user_data = user_doc.to_dict()
            stored_password = user_data.get('password')  # Assuming the password is stored as 'password'

            # Verify the password using bcrypt's checkpw method
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return True  # Credentials are valid

        # If no match found, return False
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


# Sign up function ("Username already exists." or "User successfully created!")
def signup_user(first_name, last_name, username, password, email, gender):

    try:
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if the username already exists
        existing_user = users_ref.where(filter=('username', '==', username)).limit(1).stream()

        for user in existing_user:
            return "Username already exists."  # Username already exists

        # If username is not taken, add the new user to Firestore
        new_user = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': hashed_password.decode('utf-8'),  # Store as string
            'email': email,
            'gender': gender,
        }


        # Add the document to Firestore
        users_ref.add(new_user)
        print(f"Adding new user to firestore: {new_user}")
        return "User successfully created!"

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred during sign-up."

