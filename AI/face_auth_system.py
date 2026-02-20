import face_recognition
import cv2
import numpy as np
import os
import joblib

# 📌 Configuration
FACE_DATA_DIR = "saved_models/user_faces"
if not os.path.exists(FACE_DATA_DIR):
    os.makedirs(FACE_DATA_DIR)

class FaceAIService:
    def __init__(self):
        pass

    def get_face_encoding(self, image_path_or_stream):
        """
        REGISTRATION PHASE:
        Converts an image into a 128-dimensional list of numbers.
        """
        image = face_recognition.load_image_file(image_path_or_stream)
        encodings = face_recognition.face_encodings(image, num_jitters=10)
        
        if len(encodings) == 0:
            return None 
        
        return encodings[0]

    def save_user_encoding(self, username, encoding):
        """
        Saves the face encoding to a file for a specific user.
        """
        file_path = os.path.join(FACE_DATA_DIR, f"{username}.joblib")
        joblib.dump(encoding, file_path)
        print(f"✅ Face data saved for user: {username}")
        return file_path

    def load_user_encoding(self, username):
        """
        Loads the face encoding from a file for a specific user.
        """
        file_path = os.path.join(FACE_DATA_DIR, f"{username}.joblib")
        if os.path.exists(file_path):
            return joblib.load(file_path)
        return None

    def verify_face(self, current_frame, stored_encoding, tolerance=0.5):
        """
        LOGIN PHASE:
        Compares a live webcam frame against a stored encoding.
        """
        # Ensure stored_encoding is a numpy array
        stored_encoding = np.array(stored_encoding)
        
        rgb_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        current_encodings = face_recognition.face_encodings(rgb_frame)
        
        if len(current_encodings) == 0:
            return False, "No face detected in camera"

        match = face_recognition.compare_faces([stored_encoding], current_encodings[0], tolerance=tolerance)
        distance = face_recognition.face_distance([stored_encoding], current_encodings[0])[0]
        
        if match[0]:
            return True, f"Match found (Confidence: {1 - distance:.2%})"
        else:
            return False, "Face does not match records"

# --- LIVE WEBCAM TESTING ---
if __name__ == "__main__":
    service = FaceAIService()
    
    # SETUP: Choose a name for testing
    TEST_USER = "user_7"
    IMAGE_TO_REGISTER = "7.jpg"

    # --- REGISTRATION PHASE ---
    print(f"⏳ Registering {TEST_USER} using {IMAGE_TO_REGISTER}...")
    encoding = service.get_face_encoding(IMAGE_TO_REGISTER)
    
    if encoding is not None:
        # Save this user's face "fingerprint" to disk
        service.save_user_encoding(TEST_USER, encoding)
    else:
        print("❌ Could not find face in registration image.")
        exit()

    # --- LOGIN PHASE ---
    print(f"\n⏳ Starting Login for {TEST_USER}...")
    # Load the fingerprint back from disk
    saved_fingerprint = service.load_user_encoding(TEST_USER)

    if saved_fingerprint is not None:
        video_capture = cv2.VideoCapture(0)
        print("✅ Webcam Started. Please look at the camera.")
        
        stable_match_count = 0
        REQUIRED_STABLE_FRAMES = 3 # Consecutive matches needed to login

        while True:
            ret, frame = video_capture.read()
            if not ret: break

            match, message = service.verify_face(frame, saved_fingerprint)

            if match:
                stable_match_count += 1
                color = (0, 255, 0) # Green
            else:
                stable_match_count = 0 
                color = (0, 0, 255) # Red

            # Show visual feedback
            cv2.putText(frame, f"User: {TEST_USER} | {message}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            if match:
                cv2.putText(frame, "ACCESS GRANTED! Logging in...", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            cv2.imshow('Face Login System', frame)

            # Check if we have enough stable matches to exit
            if stable_match_count >= REQUIRED_STABLE_FRAMES:
                print(f"\n🎉 ACCESS GRANTED! Welcome, {TEST_USER}.")
                # Here is where you would redirect the user or open the next page
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n❌ Login cancelled.")
                break

        video_capture.release()
        cv2.destroyAllWindows()
    else:
        print(f"❌ No registered data found for {TEST_USER}")
