from flask import render_template, request, session, redirect, url_for, flash
from pkg.agent import agent_bp
from pkg.extension import db
from pkg.model import PropertyAgent,User


@agent_bp.route("/apply/", methods=["GET","POST"])
def apply():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    user=User.query.get(session["user_id"])

    if request.method == "POST":

        license_number = request.form.get("license_number")
        agency_name = request.form.get("agency_name")

        existing = PropertyAgent.query.filter_by(
            user_id=session["user_id"]
        ).first()

        if existing:
            flash("You already submitted an agent application.", "warning")
            return redirect(url_for("user.dashboard"))

        agent = PropertyAgent(
            user_id=session["user_id"],
            license_number=license_number,
            agency_name=agency_name,
            agency_status="pending"   # ✅ important
        )

        db.session.add(agent)
        db.session.commit()

        flash("Agent application submitted. Await admin verification.", "success")
        return redirect(url_for("user.dashboard"))
    agent_pro=db.session.query(PropertyAgent).filter(PropertyAgent.user_id==user.user_id).first()

    return render_template("agent/apply_agent.html",agent_pro=agent_pro,active="agent")