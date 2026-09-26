from flask import redirect,render_template,request,session,url_for,flash,current_app,send_from_directory
from sqlalchemy import desc,asc
from pkg.main import forms
from pkg.main import main_bp
from flask_mail import Message
from pkg.extension import mail
from pkg.model import User,Property,PropertyImage,State
from markupsafe import escape
from pkg.extension import db
from collections import defaultdict
import random

@main_bp.route("/")
def homepage():
    ua = request.headers.get("User-Agent", "").lower()
     
    social_bots = [
            "facebookexternalhit",
            "facebot",
            "twitterbot",
            "linkedinbot",
            "whatsapp",
        ]
    if any(bot in ua for bot in social_bots):
        return render_template("main/social_preview.html")


    form= forms.HomeSearchForm()
    userform = forms.ContactForm()
    properties = (
        Property.query
        .filter_by(property_status="available")
        .order_by(desc(Property.created_at))
        .all()
    )

    # group properties by state
    state_groups = defaultdict(list)
    for prop in properties:
        state_groups[prop.state_id].append(prop)

    # sort states by number of listings (highest first)
    sorted_states = sorted(
        state_groups.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    featured_properties = []

    # pick one random property from each top state
    for state_id, props in sorted_states:
        featured_properties.append(random.choice(props))
        if len(featured_properties) == 6:
            break

    # if still fewer than 6, fill with random remaining properties
    if len(featured_properties) < 6:
        remaining = [p for p in properties if p not in featured_properties]
        random.shuffle(remaining)

        for prop in remaining:
            featured_properties.append(prop)
            if len(featured_properties) == 6:
                break

    covers = {}
    for prop in featured_properties:
        cover = (
            PropertyImage.query
            .filter_by(property_id=prop.property_id,is_primary=True)
            .first()
        )
        if not cover:
            cover =(
                PropertyImage.query.filter_by(
                    property_id=prop.property_id
                ).order_by(asc(PropertyImage.image_id))
                .first()
            )
        if cover and cover.image_url:
            covers[prop.property_id] =(
                cover.image_url
            )
        else:
            covers[prop.property_id] = (
                "uploads/default-property.jpg"
            )

    # print("MAIL_DEFAULT_SENDER:", current_app.config.get("MAIL_DEFAULT_SENDER"))
    # print("PEA_BRIDGE_EMAIL:", current_app.config.get("PEA_BRIDGE_EMAIL"))
    return render_template(
        "main/homepage.html",
        form=form,
        featured_properties=featured_properties,
        covers=covers,
        userform=userform,
        active="homepage"
    )

@main_bp.route("/robots.txt")
def robots_txt():
    return send_from_directory(current_app.static_folder,"robots.txt")


@main_bp.route('/privacy/')
def privacy():
    return render_template('main/privacy.html')


@main_bp.route("/listing/<int:property_id>/")
def home_property_detail(property_id):
    prop = Property.query.get_or_404(property_id)

    images = (
        PropertyImage.query
        .filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id))
        .all()
    )

    next_page = request.args.get("next", "explore")
   
    return render_template(
        "main/home_property_detail.html",
        prop=prop,
        images=images,
        next_page=next_page,
    )


@main_bp.route("/search_view/")
def search_view():
    property_type = request.args.get("type", "").strip().lower()
    location = request.args.get("location", "").strip()
    budget = request.args.get("budget", "").strip()

    # if everything is empty, return nothing
    if not property_type and not location and not budget:
        return """
                <div class="alert alert-danger mt-3 search-message"
                    data-timeout='true'>
                please fill in the space.
                </div>

            """
    # if location is provided, check state first
    state = None
    if location:
        state = State.query.filter(State.state_name.ilike(f"%{location}%")).first()

        if not state:
            return """
                    <div class="alert alert-danger mt-3 searcH-message"
                        data-timeout="true>
                        State not found.
                    </div>
                    """

    query = Property.query.filter(Property.property_status == "available")

    # if state exists, filter by that exact state
    if state:
        query = query.filter(Property.state_id == state.state_id)

    # optional type filter
    if property_type:
        query = query.filter(Property.property_type == property_type)

    # optional budget filter
    if budget == "under_20m":
        query = query.filter(Property.price < 20000000)
    elif budget == "20m_50m":
        query = query.filter(Property.price >= 20000000, Property.price <= 50000000)
    elif budget == "50m_100m":
        query = query.filter(Property.price >= 50000000, Property.price <= 100000000)
    elif budget == "100m_plus":
        query = query.filter(Property.price > 100000000)

    results = query.order_by(desc(Property.created_at)).all()

    if not results:
        return """
                <div class="alert alert-warning mt-3 search-message"
                    data-timeout="true">
                    No property found for this search.
                </div>
                """

    html = '<div class="row g-3 mt-2">'

    for prop in results:
        cover = (
            PropertyImage.query
            .filter_by(property_id=prop.property_id)
            .order_by(asc(PropertyImage.image_id))
            .first()
        )

        image_url = cover.image_url if cover else "property_images/default_property.png"
        state_name = prop.states.state_name if prop.states else "No State"

        html += f"""
        <div class="col-12 col-md-6 col-lg-4">
          <div class="city">
            <a href="/listing/{prop.property_id}/" class="city-link">
              <img src="/static/{image_url}" alt="{prop.property_title}">
            </a>
            <div class="label">
              <h5 class="fw-bold mb-1">{prop.property_title or "Property"}</h5>
              <div class="small">{state_name} • ₦ {prop.price or 0:,.0f}</div>
            </div>
          </div>
        </div>
        """

    html += "</div>"
    return html


@main_bp.route(
    "/contact/send/",
    methods=["POST"]
)
def send_contact_message():

    userform = forms.ContactForm()

    if userform.validate_on_submit():

        try:
            # =========================
            # ORIGINAL TEXT VALUES
            # =========================

            fullname = userform.fullname.data.strip()
            email = userform.email.data.strip()
            subject = userform.subject.data.strip()
            message = userform.message.data.strip()


            # =========================
            # SAFE HTML VALUES
            # =========================

            safe_fullname = escape(fullname)
            safe_email = escape(email)
            safe_subject = escape(subject)
            safe_message = escape(message)


            # =========================
            # CREATE EMAIL
            # =========================

            msg = Message(
                subject=f"Flexy Properties Contact: {subject}",
                recipients=[
                    current_app.config["FLEXY_EMAIL"]
                ],
                sender=current_app.config[
                    "MAIL_DEFAULT_SENDER"
                ],
                reply_to=email
            )
            
            # =========================
            # PLAIN TEXT VERSION
            # =========================

            msg.body = f"""
                New message from Flexy Properties contact form

                Full Name: {fullname}
                Email: {email}
                Subject: {subject}

                Message:
                {message}

                ---
                Flexy Properties
                Website Contact Form
                """


            # =========================
            # HTML VERSION
            # =========================

            msg.html = f"""
                <!DOCTYPE html>

                <html lang="en">

                <head>

                    <meta charset="UTF-8">

                    <meta
                        name="viewport"
                        content="width=device-width, initial-scale=1.0"
                    >

                    <title>
                        Flexy Properties Contact Message
                    </title>

                </head>


                <body style="
                    margin:0;
                    padding:0;
                    background-color:#f4f7f6;
                    font-family:Arial, Helvetica, sans-serif;
                    color:#334155;
                ">

                <table
                    role="presentation"
                    width="100%"
                    cellspacing="0"
                    cellpadding="0"
                    border="0"
                    style="
                        width:100%;
                        background-color:#f4f7f6;
                        padding:40px 15px;
                    "
                >

                    <tr>

            <td align="center">

                <table
                    role="presentation"
                    width="100%"
                    cellspacing="0"
                    cellpadding="0"
                    border="0"
                    style="
                        width:100%;
                        max-width:620px;
                        background:#ffffff;
                        border:1px solid #e2e8f0;
                        border-radius:12px;
                        overflow:hidden;
                    "
                >


                <!-- HEADER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#0f172a;
                            padding:30px 25px;
                        "
                    >

                        <div style="
                            font-size:27px;
                            font-weight:700;
                            color:#ffffff;
                        ">

                            Flexy

                            <span style="
                                color:#22c55e;
                            ">
                                Properties
                            </span>

                        </div>


                        <p style="
                            margin:8px 0 0;
                            color:#cbd5e1;
                            font-size:13px;
                        ">
                            Website Contact Notification
                        </p>

                    </td>

                </tr>


                <!-- CONTENT -->

                <tr>

                    <td style="
                        padding:35px;
                    ">

                        <h2 style="
                            margin:0 0 8px;
                            color:#0f172a;
                            font-size:23px;
                        ">
                            New Contact Message
                        </h2>


                        <p style="
                            margin:0 0 28px;
                            color:#64748b;
                            font-size:14px;
                            line-height:1.7;
                        ">
                            A visitor submitted a message
                            through the Flexy Properties
                            contact form.
                        </p>


                        <!-- CONTACT DETAILS -->

                        <table
                            role="presentation"
                            width="100%"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                width:100%;
                                border-collapse:collapse;
                            "
                        >

                            <tr>

                                <td style="
                                    width:120px;
                                    padding:12px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                    color:#64748b;
                                    font-size:14px;
                                ">
                                    Full Name
                                </td>

                                <td style="
                                    padding:12px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                    color:#0f172a;
                                    font-size:14px;
                                    font-weight:600;
                                ">
                                    {safe_fullname}
                                </td>

                            </tr>


                            <tr>

                                <td style="
                                    padding:12px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                    color:#64748b;
                                    font-size:14px;
                                ">
                                    Email
                                </td>

                                <td style="
                                    padding:12px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                    font-size:14px;
                                ">

                                    <a
                                        href="mailto:{safe_email}"
                                        style="
                                            color:#16a34a;
                                            text-decoration:none;
                                            font-weight:600;
                                        "
                                    >
                                        {safe_email}
                                    </a>

                                </td>

                            </tr>


                            <tr>

                                <td style="
                                    padding:12px 0;
                                    color:#64748b;
                                    font-size:14px;
                                ">
                                    Subject
                                </td>

                                <td style="
                                    padding:12px 0;
                                    color:#0f172a;
                                    font-size:14px;
                                    font-weight:600;
                                ">
                                    {safe_subject}
                                </td>

                            </tr>

                        </table>


                        <!-- MESSAGE -->

                        <div style="
                            margin-top:28px;
                        ">

                            <p style="
                                margin:0 0 10px;
                                color:#0f172a;
                                font-size:14px;
                                font-weight:700;
                            ">
                                Message
                            </p>


                            <div style="
                                background:#f8fafc;
                                border:1px solid #e2e8f0;
                                border-left:
                                    4px solid #22c55e;
                                padding:18px;
                                border-radius:7px;
                                color:#475569;
                                font-size:14px;
                                line-height:1.7;
                                white-space:pre-wrap;
                            ">{safe_message}</div>

                        </div>


                        <!-- REPLY BUTTON -->

                        <table
                            role="presentation"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                margin-top:28px;
                            "
                        >

                            <tr>

                                <td
                                    bgcolor="#16a34a"
                                    style="
                                        border-radius:7px;
                                    "
                                >

                                    <a
                                        href="mailto:{safe_email}"
                                        style="
                                            display:inline-block;
                                            padding:13px 24px;
                                            color:#ffffff;
                                            text-decoration:none;
                                            font-size:14px;
                                            font-weight:700;
                                        "
                                    >
                                        Reply to Customer
                                    </a>

                                </td>

                            </tr>

                        </table>

                    </td>

                </tr>


                <!-- FOOTER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#f8fafc;
                            border-top:
                                1px solid #e2e8f0;
                            padding:22px 25px;
                        "
                    >

                        <p style="
                            margin:0 0 5px;
                            color:#64748b;
                            font-size:12px;
                            font-weight:600;
                        ">
                            Flexy Properties
                        </p>


                        <p style="
                            margin:0;
                            color:#94a3b8;
                            font-size:11px;
                            line-height:1.6;
                        ">
                            This notification was generated
                            from the Flexy Properties website
                            contact form.
                        </p>

                    </td>

                </tr>

            </table>

        </td>

    </tr>

</table>

</body>

</html>
"""

            mail.send(msg)

            flash(
                "Your message has been sent successfully.",
                "success"
            )


        except Exception:

            current_app.logger.exception(
                "CONTACT FORM MAIL ERROR"
            )

            flash(
                "Message could not be sent right now. "
                "Please try again later.",
                "danger"
            )


    else:

        flash(
            "Please fill the form correctly before sending.",
            "warning"
        )


    return redirect(
        url_for("main.homepage")
    )