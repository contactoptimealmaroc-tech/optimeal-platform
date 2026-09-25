import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.db import SessionLocal
from app.core.models import User, ClientProfile
from app.core.security import hash_password

p=argparse.ArgumentParser(); p.add_argument('--email',required=True); p.add_argument('--password',required=True); p.add_argument('--role',choices=['CLIENT','CHEF','NUTRITION','ADMIN'],required=True); p.add_argument('--name',default=''); args=p.parse_args()
db=SessionLocal()
try:
    email=args.email.lower().strip()
    if db.query(User).filter(User.email==email).first(): raise SystemExit('USER_ALREADY_EXISTS')
    u=User(email=email,password_hash=hash_password(args.password),role=args.role,is_active=True); db.add(u); db.flush()
    if args.role=='CLIENT': db.add(ClientProfile(user_id=u.id,full_name=args.name))
    db.commit(); print(f'created user id={u.id} role={u.role}')
finally: db.close()
