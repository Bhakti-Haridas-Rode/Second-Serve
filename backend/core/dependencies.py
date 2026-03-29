from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print("TOKEN RECEIVED:", token)


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("SECRET KEY:", SECRET_KEY)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


#-------Role based access control dependency -----------

def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this role"
            )
        return user
    return role_checker
