from flask import current_app
from flask_mail import Message
from pkg.extension import mail
from markupsafe import escape
from urllib.parse import quote

def clean_header(value):
    return (
        str(value or "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .strip()
    )


def send_interest_confirmation(
    email,
    username,
    property_title,
):

    try:

        recipient_email = str(email).strip()
        safe_username = escape(username)
        safe_property_title = escape(property_title)

        msg = Message(
            subject="Property Interest Request Received",
            recipients=[recipient_email],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )

        msg.body = f"""
            Hello {username},

We have received your interest request for:

{property_title}

Your request has been submitted successfully and is
currently awaiting review.

We will notify you when there is an update to your
request.

Thank you for using Flexy Properties.

Flexy Properties
"""

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
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
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Property Interest Request
            </p>

        </td>
    </tr>


    <!-- CONTENT -->

    <tr>
        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 20px;
                color:#0f172a;
                font-size:24px;
            ">
                Interest Request Received
            </h1>

            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Hello <strong>{safe_username}</strong>,
            </p>

            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                We have successfully received your
                interest request for the property below.
            </p>


            <!-- PROPERTY -->

            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                style="
                    margin:25px 0;
                    background:#f8fafc;
                    border:1px solid #e2e8f0;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:18px;
                        color:#475569;
                        font-size:14px;
                    ">

                        <span style="
                            color:#64748b;
                            font-size:12px;
                        ">
                            PROPERTY
                        </span>

                        <br>

                        <strong style="
                            color:#0f172a;
                            font-size:16px;
                        ">
                            {safe_property_title}
                        </strong>

                    </td>

                </tr>

            </table>


            <!-- STATUS -->

            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                style="
                    margin:25px 0;
                    background:#fffbeb;
                    border:1px solid #fde68a;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:17px;
                        color:#92400e;
                        font-size:14px;
                        line-height:1.6;
                    ">

                        <strong>
                            Status: Awaiting Review
                        </strong>

                        <br>

                        Our team will review your request.
                        We'll notify you when its status
                        changes.

                    </td>

                </tr>

            </table>


            <p style="
                margin:25px 0 0;
                color:#64748b;
                font-size:13px;
                line-height:1.7;
            ">
                You don't need to submit another request
                for the same property while this request
                is being reviewed.
            </p>

        </td>
    </tr>


    <!-- FOOTER -->

    <tr>

        <td
            align="center"
            style="
                background:#f8fafc;
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties
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
        print("========== CUSTOMER EMAIL ==========")
        print("TO:", msg.recipients)
        print("SUBJECT:", msg.subject)
        print("====================================")


        mail.send(msg)
    except Exception:
        current_app.logger.exception(
            "INTEREST CONFIRMATION EMAIL ERROR"
        )


def send_new_interest_admin_email(
    customer_name,
    customer_email,
    property_title,
    property_id
):

    try:
        

        msg = Message(
            subject=(
                f"New Property Interest: "
                f'{property_title}'
            ),
            recipients=[current_app.config["FLEXY_EMAIL"]],
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            reply_to=customer_email
        )


        msg.body = f"""

                New property interest request

Customer: {customer_name}
Email: {customer_email}

Property:
{property_title}

Property ID:
{property_id}

Please sign in to the Flexy Properties administration
panel to review the request.

Flexy Properties
"""

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
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
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Administration Notification
            </p>

        </td>

    </tr>


    <!-- CONTENT -->

    <tr>

        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 10px;
                color:#0f172a;
                font-size:24px;
            ">
                New Interest Request
            </h1>

            <p style="
                margin:0 0 25px;
                color:#64748b;
                font-size:14px;
                line-height:1.7;
            ">
                A customer has submitted a new property
                interest request.
            </p>


            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="border-collapse:collapse;"
            >

                <tr>

                    <td style="
                        padding:12px 0;
                        border-bottom:
                            1px solid #e2e8f0;
                        color:#64748b;
                        width:130px;
                        font-size:14px;
                    ">
                        Customer
                    </td>

                    <td style="
                        padding:12px 0;
                        border-bottom:
                            1px solid #e2e8f0;
                        color:#0f172a;
                        font-weight:600;
                        font-size:14px;
                    ">
                        {customer_name}
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
                            href="mailto:{customer_email}"
                            style="
                                color:#16a34a;
                                text-decoration:none;
                            "
                        >
                            {customer_email}
                        </a>

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
                        Property
                    </td>

                    <td style="
                        padding:12px 0;
                        border-bottom:
                            1px solid #e2e8f0;
                        color:#0f172a;
                        font-weight:600;
                        font-size:14px;
                    ">
                        {property_title}
                    </td>

                </tr>


                <tr>

                    <td style="
                        padding:12px 0;
                        color:#64748b;
                        font-size:14px;
                    ">
                        Property ID
                    </td>

                    <td style="
                        padding:12px 0;
                        color:#0f172a;
                        font-size:14px;
                    ">
                        #{property_id}
                    </td>

                </tr>

            </table>


            <div style="
                margin-top:28px;
                background:#f0fdf4;
                border:1px solid #bbf7d0;
                border-radius:8px;
                padding:17px;
                color:#166534;
                font-size:14px;
                line-height:1.6;
            ">

                <strong>Action required</strong>

                <br>

                Sign in to the Flexy Properties
                administration panel to review this
                interest request.

            </div>

        </td>

    </tr>


    <!-- FOOTER -->

    <tr>

        <td
            align="center"
            style="
                background:#f8fafc;
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties Administration
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

        print("============ ADMIN EMAIL ===========")
        print("TO:", msg.recipients)
        print("SUBJECT:", msg.subject)
        print("REPLY TO:", msg.reply_to)
        print("====================================")


        mail.send(msg)

    except Exception:
        current_app.logger.exception(
            "NEW INTEREST ADMIN EMAIL ERROR"
        )

def send_interest_approved_email(
    email,
    username,
    property_title,
    listing_type,
    property_id
):

    try:

       
        recipient_email = str(email).strip()

        listing_type =(
            str(listing_type)
            .strip()
            .upper()
        )

        if listing_type == "SALE":
            action = "purchase"

            action_title = "Purchase Request Approved"

            approval_message = (
                "Your request to purchase this "
                "property has been approved."
            )

            next_step_message = (
                "Flexy Properties will guide you "
                "through the next steps regarding "
                "the property purchase."
            )


        elif listing_type == "RENT":

            action = "rent"

            action_title = "Rental Request Approved"

            approval_message = (
                "Your request to rent this "
                "property has been approved."
            )

            next_step_message = (
                "Flexy Properties will guide you "
                "through the next steps regarding "
                "the property rental."
            )


        else:

            raise ValueError(
                "Invalid property listing type "
                "for interest approval email."
            )


        safe_name = escape(
            str(username)
        )

        safe_title = escape(
            str(property_title)
        )

        safe_action_title = escape(
            action_title
        )

        safe_approval_message = escape(
            approval_message
        )

        safe_next_step = escape(
            next_step_message
        )

          # ==========================================
        # WHATSAPP
        # ==========================================

        whatsapp_message = quote(
            f"Hello Flexy Properties, "
            f"my request to {action} "
            f"'{property_title}' has been approved. "
            f"I would like to know the next steps."
        )


        whatsapp_url = (
            "https://wa.me/2349017096022"
            f"?text={whatsapp_message}"
        )


        # ==========================================
        # EMAIL
        # ==========================================

        msg = Message(
            subject=(
                f"{action_title} - Flexy Properties"
            ),
            recipients=[
                recipient_email
            ],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )


        # ==========================================
        # PLAIN TEXT VERSION
        # ==========================================

        msg.body = f"""
Hello {username},

Good news!

{approval_message}

Property: {property_title}
Listing Type: {"For Sale" if listing_type == "SALE" else "For Rent"}

{next_step_message}

Please do not make payments or transfer funds based solely on unofficial messages. Follow the communication and instructions provided through Flexy Properties.

If you need assistance, contact Flexy Properties through our official WhatsApp number.

Thank you for using Flexy Properties.

Flexy Properties
www.flexyproperties.org
"""


        # ==========================================
        # HTML VERSION
        # ==========================================

        msg.html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

</head>


<body
    style="
        margin:0;
        padding:0;
        background:#f2f4f7;
        font-family:Arial,Helvetica,sans-serif;
        color:#344054;
    "
>


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        background:#f2f4f7;
        padding:32px 15px;
    "
>

<tr>

<td align="center">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:600px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        box-shadow:
            0 4px 14px
            rgba(16,24,40,.08);
    "
>


    <!-- HEADER -->

    <tr>

        <td
            style="
                background:#101828;
                padding:25px 30px;
                text-align:center;
            "
        >

            <div
                style="
                    color:#ffffff;
                    font-size:22px;
                    font-weight:700;
                "
            >
                Flexy Properties
            </div>

            <div
                style="
                    color:#98a2b3;
                    font-size:12px;
                    margin-top:5px;
                "
            >
                Property Marketing & Marketplace
            </div>

        </td>

    </tr>



    <!-- CONTENT -->

    <tr>

        <td style="padding:35px 30px;">


            <!-- SUCCESS ICON -->

            <div
                style="
                    width:56px;
                    height:56px;
                    line-height:56px;
                    margin:0 auto 20px;
                    background:#ecfdf3;
                    border-radius:50%;
                    text-align:center;
                    color:#079455;
                    font-size:26px;
                    font-weight:bold;
                "
            >
                ✓
            </div>


            <h2
                style="
                    margin:0 0 10px;
                    text-align:center;
                    color:#101828;
                    font-size:22px;
                "
            >
                {safe_action_title}
            </h2>


            <p
                style="
                    margin:0 0 28px;
                    text-align:center;
                    color:#667085;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Good news! Your property interest
                request has been approved.
            </p>


            <p
                style="
                    margin:0 0 18px;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Hello <strong>{safe_name}</strong>,
            </p>


            <p
                style="
                    margin:0 0 24px;
                    color:#475467;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                {safe_approval_message}
            </p>



            <!-- PROPERTY INFORMATION -->

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                border="0"
                style="
                    margin-bottom:24px;
                    background:#f9fafb;
                    border:1px solid #eaecf0;
                    border-radius:10px;
                "
            >

                <tr>

                    <td style="padding:18px;">


                        <div style="margin-bottom:14px;">

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Property
                            </div>

                            <div
                                style="
                                    margin-top:4px;
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                "
                            >
                                {safe_title}
                            </div>

                        </div>


                        <div>

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Listing Type
                            </div>

                            <div
                                style="
                                    margin-top:4px;
                                    color:#079455;
                                    font-size:14px;
                                    font-weight:bold;
                                "
                            >

                                {
                                    "For Sale"
                                    if listing_type == "SALE"
                                    else "For Rent"
                                }

                            </div>

                        </div>


                    </td>

                </tr>

            </table>



            <!-- NEXT STEPS -->

            <div
                style="
                    padding:16px 18px;
                    margin-bottom:22px;
                    background:#ecfdf3;
                    border-left:4px solid #079455;
                    border-radius:7px;
                "
            >

                <div
                    style="
                        margin-bottom:6px;
                        color:#067647;
                        font-size:12px;
                        font-weight:bold;
                        text-transform:uppercase;
                    "
                >
                    What Happens Next?
                </div>


                <div
                    style="
                        color:#475467;
                        font-size:13px;
                        line-height:1.7;
                    "
                >
                    {safe_next_step}
                </div>

            </div>



            <!-- SAFETY NOTICE -->

            <div
                style="
                    padding:15px 17px;
                    margin-bottom:25px;
                    background:#fffaeb;
                    border-left:4px solid #f79009;
                    border-radius:7px;
                "
            >

                <strong
                    style="
                        display:block;
                        margin-bottom:5px;
                        color:#93370d;
                        font-size:12px;
                    "
                >
                    Important
                </strong>


                <span
                    style="
                        color:#475467;
                        font-size:12px;
                        line-height:1.7;
                    "
                >
                    Do not make payments or transfer
                    funds based solely on unofficial
                    messages. Follow the communication
                    and instructions provided through
                    Flexy Properties.
                </span>

            </div>



            <!-- WHATSAPP -->

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                border="0"
            >

                <tr>

                    <td align="center">

                        <a
                            href="{whatsapp_url}"
                            target="_blank"
                            style="
                                display:inline-block;
                                padding:13px 22px;
                                background:#079455;
                                border-radius:8px;
                                color:#ffffff;
                                font-size:13px;
                                font-weight:bold;
                                text-decoration:none;
                            "
                        >
                            Contact Flexy Properties
                            on WhatsApp
                        </a>

                    </td>

                </tr>

            </table>


        </td>

    </tr>



    <!-- FOOTER -->

    <tr>

        <td
            style="
                padding:20px 30px;
                background:#f9fafb;
                border-top:1px solid #eaecf0;
                text-align:center;
            "
        >

            <div
                style="
                    color:#667085;
                    font-size:12px;
                    line-height:1.6;
                "
            >
                Flexy Properties
                <br>
                Property Marketplace
            </div>


            <div
                style="
                    margin-top:7px;
                    color:#98a2b3;
                    font-size:11px;
                "
            >
                www.flexyproperties.org
            </div>

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

        return True


    except Exception:

        current_app.logger.exception(
            "INTEREST APPROVAL EMAIL ERROR"
        )

        return False

def send_interest_declined_email(
    email,
    username,
    property_title
):

    try:

        recipient_email = str(email).strip()
        safe_username = escape(username)
        safe_property_title = escape(property_title)

        msg = Message(
            subject="Update on Your Property Interest Request",
            recipients=[recipient_email],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )

        msg.body = f"""

        Hello {username},

There has been an update regarding your interest
request for:

{property_title}

Unfortunately, we are unable to proceed with this
interest request at this time.

You can continue exploring other available properties
on Flexy Properties.

Thank you for your interest.

Flexy Properties
"""

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        max-width:620px;
        background:#ffffff;
        border:1px solid #e2e8f0;
        border-radius:12px;
        overflow:hidden;
    "
>

    <tr>

        <td
            align="center"
            style="
                background:#0f172a;
                padding:30px;
            "
        >

            <div style="
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Property Interest Update
            </p>

        </td>

    </tr>


    <tr>

        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 20px;
                color:#0f172a;
                font-size:24px;
            ">
                Interest Request Update
            </h1>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Hello <strong>{safe_username}</strong>,
            </p>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                There has been an update regarding your
                interest request for:
            </p>


            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                style="
                    margin:25px 0;
                    background:#fff7ed;
                    border:1px solid #fed7aa;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:20px;
                        color:#9a3412;
                    ">

                        <strong style="
                            display:block;
                            font-size:16px;
                            margin-bottom:6px;
                        ">
                            {safe_property_title}
                        </strong>

                        <span style="
                            font-size:14px;
                        ">
                            Status:
                            <strong>Declined</strong>
                        </span>

                    </td>

                </tr>

            </table>


            <p style="
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                Unfortunately, we are unable to proceed
                with this interest request at this time.
            </p>


            <p style="
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                You can continue exploring other
                available properties on
                Flexy Properties.
            </p>


            <p style="
                margin:25px 0 0;
                color:#64748b;
                font-size:13px;
                line-height:1.7;
            ">
                Thank you for your interest in
                Flexy Properties.
            </p>

        </td>

    </tr>


    <tr>

        <td
            align="center"
            style="
                background:#f8fafc;
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties
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

    except Exception:
        current_app.logger.exception(
            "INTEREST DECLINED EMAIL ERROR"
        )

def send_account_verified_email(
    email,
    username
):

    try:

        recipient_email = str(email).strip()
        safe_username = escape(username)

        msg = Message(
            subject="Your Flexy Properties Account Has Been Verified.",
            recipients=[recipient_email],
            sender=current_app.config["MAIL_DEFAULT_SENDER"]
        )

        msg.body = f"""

        Hello {username},

Your Flexy Properties account has been successfully verified.

Your account verification has been completed, and your account
is now recognized as verified on Flexy Properties.

You can continue exploring available properties and managing
your property interests.

Thank you for being part of Flexy Properties.

Flexy Properties
"""


        # ==========================
        # HTML
        # ==========================

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
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
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Account Notification
            </p>

        </td>
    </tr>


    <!-- CONTENT -->

    <tr>

        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 20px;
                color:#0f172a;
                font-size:24px;
            ">
                Account Verified
            </h1>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Hello <strong>{safe_username}</strong>,
            </p>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Your Flexy Properties account has been
                successfully verified.
            </p>


            <!-- STATUS -->

            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    margin:25px 0;
                    background:#f0fdf4;
                    border:1px solid #bbf7d0;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:20px;
                        color:#166534;
                        font-size:14px;
                        line-height:1.7;
                    ">

                        <strong style="
                            display:block;
                            font-size:16px;
                            margin-bottom:5px;
                        ">
                            ✓ Verification Complete
                        </strong>

                        Your account is now recognized
                        as verified on Flexy Properties.

                    </td>

                </tr>

            </table>


            <p style="
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                You can continue exploring available
                properties and managing your property
                interests.
            </p>


            <p style="
                margin:25px 0 0;
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                Thank you for being part of
                <strong>Flexy Properties</strong>.
            </p>

        </td>

    </tr>


    <!-- FOOTER -->

    <tr>

        <td
            align="center"
            style="
                background:#f8fafc;
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties
            </p>

            <p style="
                margin:7px 0 0;
                color:#94a3b8;
                font-size:11px;
            ">
                Helping you find the right property.
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

    except Exception:
        current_app.logger.exception(
            "ACCOUNT VERIFIED EMAIL ERROR"
        )

def send_account_suspended_email(
    email,
    username
):

    try:

        recipient_email = str(email).strip()
        safe_username = escape(username)

        msg = Message(
            subject="Important Update About Your Flexy Properties Account.",
            recipients=[recipient_email],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )

        msg.body = f"""

        Hello {username},

Your Flexy Properties account has been suspended.

While your account is suspended, access to certain account
features may be restricted.

If you believe this action requires clarification, please
contact Flexy Properties for assistance.

Your account may be restored after review where appropriate.

Thank you.

Flexy Properties
"""


        # ==========================
        # HTML
        # ==========================

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
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
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Account Notification
            </p>

        </td>

    </tr>


    <!-- CONTENT -->

    <tr>

        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 20px;
                color:#0f172a;
                font-size:24px;
            ">
                Account Suspended
            </h1>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Hello <strong>{safe_username}</strong>,
            </p>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                We're writing to inform you that your
                Flexy Properties account has been
                suspended.
            </p>


            <!-- SUSPENSION NOTICE -->

            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    margin:25px 0;
                    background:#fff7ed;
                    border:1px solid #fed7aa;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:20px;
                        color:#9a3412;
                        font-size:14px;
                        line-height:1.7;
                    ">

                        <strong style="
                            display:block;
                            font-size:16px;
                            margin-bottom:5px;
                        ">
                            Account Status: Suspended
                        </strong>

                        While your account is suspended,
                        access to certain account
                        features may be restricted.

                    </td>

                </tr>

            </table>


            <p style="
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                If you believe this action requires
                clarification, please contact Flexy
                Properties for assistance.
            </p>


            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    margin-top:25px;
                    background:#f8fafc;
                    border:1px solid #e2e8f0;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:18px;
                        color:#475569;
                        font-size:13px;
                        line-height:1.7;
                    ">

                        Your account may be restored
                        after review where appropriate.
                        You will receive another
                        notification if your account is
                        reactivated.

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
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties
            </p>

            <p style="
                margin:7px 0 0;
                color:#94a3b8;
                font-size:11px;
            ">
                Account & Security Notification
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

    except Exception:
        
        current_app.logger.exception(
            "ACCOUNT SUSPENDED EMAIL ERROR"
        )


def send_account_reactivated_email(
    email,
    username
):

    try:
        

        recipient_email = str(email).strip()
        safe_username = escape(username)

        msg = Message(
            subject="Your Flexy Properties Account Has Been Reactivated",
            recipients=[recipient_email],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )

        msg.body = f"""

        Hello {username},

Your Flexy Properties account has been reactivated.

Your account is active again, and you can continue using the
available features of Flexy Properties.

You can sign in and continue exploring properties and managing
your property interests.

Welcome back to Flexy Properties.

Flexy Properties
"""


        # ==========================
        # HTML
        # ==========================

        msg.html = f"""
<!DOCTYPE html>

<html lang="en">

<body style="
    margin:0;
    padding:0;
    background:#f4f7f6;
    font-family:Arial, Helvetica, sans-serif;
">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
        background:#f4f7f6;
        padding:40px 15px;
    "
>

<tr>
<td align="center">

<table
    width="100%"
    cellspacing="0"
    cellpadding="0"
    border="0"
    style="
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
                color:#ffffff;
                font-size:27px;
                font-weight:700;
            ">
                Flexy
                <span style="color:#22c55e;">
                    Properties
                </span>
            </div>

            <p style="
                margin:8px 0 0;
                color:#cbd5e1;
                font-size:13px;
            ">
                Account Notification
            </p>

        </td>

    </tr>


    <!-- CONTENT -->

    <tr>

        <td style="padding:38px 35px;">

            <h1 style="
                margin:0 0 20px;
                color:#0f172a;
                font-size:24px;
            ">
                Account Reactivated
            </h1>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Hello <strong>{safe_username}</strong>,
            </p>


            <p style="
                color:#475569;
                font-size:15px;
                line-height:1.7;
            ">
                Your Flexy Properties account has been
                successfully reactivated.
            </p>


            <!-- STATUS -->

            <table
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    margin:25px 0;
                    background:#f0fdf4;
                    border:1px solid #bbf7d0;
                    border-radius:8px;
                "
            >

                <tr>

                    <td style="
                        padding:20px;
                        color:#166534;
                        font-size:14px;
                        line-height:1.7;
                    ">

                        <strong style="
                            display:block;
                            font-size:16px;
                            margin-bottom:5px;
                        ">
                            ✓ Account Status: Active
                        </strong>

                        Your account access has been
                        restored.

                    </td>

                </tr>

            </table>


            <p style="
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                You can sign in and continue exploring
                available properties and managing your
                property interests.
            </p>


            <p style="
                margin:25px 0 0;
                color:#475569;
                font-size:14px;
                line-height:1.7;
            ">
                Welcome back to
                <strong>Flexy Properties</strong>.
            </p>

        </td>

    </tr>


    <!-- FOOTER -->

    <tr>

        <td
            align="center"
            style="
                background:#f8fafc;
                border-top:1px solid #e2e8f0;
                padding:24px;
            "
        >

            <p style="
                margin:0;
                color:#64748b;
                font-size:12px;
                font-weight:600;
            ">
                Flexy Properties
            </p>

            <p style="
                margin:7px 0 0;
                color:#94a3b8;
                font-size:11px;
            ">
                Helping you find the right property.
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
       
    except Exception:
        
        current_app.logger.exception(
            "ACCOUNT REACTIVATED EMAIL ERROR"
        )


def send_property_submission_confirmation(
    email,
    landlord_name,
    property_title,
    listing_type,
    reference_number
):


    try:

        recipients_email = str(email).strip()
        safe_name = escape(landlord_name)
        safe_title = escape(property_title)
        safe_reference = escape(reference_number)
        listing_label = {
            "SALE": "For Sale",
            "RENT": "For Rent"
        }.get(
            str(listing_type).lower(),
            str(listing_type).title()
        )

        safe_listing = escape(listing_label)

        msg = Message(
            subject=(
                f"Property Submission Received - "
                f"{reference_number}"
            ),
            recipients=[recipients_email],
            sender=current_app.config[
                    "MAIL_DEFAULT_SENDER"
                ]
        
        )

        msg.body = f"""

        Hello {landlord_name},

Thank you for submitting your property to Flexy Properties.

We have successfully received your property submission.

Property:
{property_title}

Submission Reference:
{reference_number}

Your property is currently awaiting review by the Flexy Properties team.

Please keep your submission reference number. It will help us identify your property if you contact us regarding this submission.

Please note that submitting a property does not mean that it has automatically been approved or published.

Our team may contact you if additional information or verification is required.

Thank you for choosing Flexy Properties.

Flexy Properties
"""

        # ==========================
        # HTML
        # ==========================

        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <body style="
            margin:0;
            padding:0;
            background:#f5f7fa;
            font-family:Arial,Helvetica,sans-serif;
        ">

            <div style="
                max-width:620px;
                margin:30px auto;
                background:#ffffff;
                border-radius:12px;
                overflow:hidden;
                border:1px solid #e3e8ee;
            ">

                <div style="
                    background:#0b1f33;
                    padding:32px 25px;
                    text-align:center;
                ">

                    <div style="
                        color:#ffffff;
                        font-size:22px;
                        font-weight:700;
                    ">
                        Flexy Properties
                    </div>

                    <div style="
                        color:#b8c6d3;
                        font-size:13px;
                        margin-top:6px;
                    ">
                        Property Submission Confirmation
                    </div>

                </div>


                <div style="
                    padding:35px 30px;
                    color:#374151;
                    line-height:1.7;
                ">

                    <h2 style="
                        color:#0b1f33;
                        margin-top:0;
                        font-size:21px;
                    ">
                        Property Submission Received
                    </h2>

                    <p>
                        Hello <strong>{safe_name}</strong>,
                    </p>

                    <p>
                        Thank you for submitting your property
                        to Flexy Properties. We have successfully
                        received your submission.
                    </p>


                    <div style="
                        background:#f6f9f7;
                        border:1px solid #dcebe2;
                        border-radius:10px;
                        padding:20px;
                        margin:25px 0;
                    ">

                        <div style="
                            font-size:12px;
                            color:#6b7280;
                            text-transform:uppercase;
                            margin-bottom:5px;
                        ">
                            Property
                        </div>

                        <div style="
                            color:#0b1f33;
                            font-weight:700;
                            margin-bottom:18px;
                        ">
                            {safe_title}
                        </div>

                        <div style="
                            font-size:12px;
                            color:#6b7280;
                            text-transform:uppercase;
                            margin-bottom:5px;
                        ">
                            Listing Purpose
                        </div>

                        <div style="
                            color:#0b1f33;
                            font-weight:700;
                            margin-bottom:18px;
                        ">
                            {safe_listing}
                        </div>


                        <div style="
                            font-size:12px;
                            color:#6b7280;
                            text-transform:uppercase;
                            margin-bottom:5px;
                        ">
                            Submission Reference
                        </div>

                        <div style="
                            color:#198754;
                            font-size:20px;
                            font-weight:700;
                        ">
                            {safe_reference}
                        </div>

                    </div>


                    <p>
                        Your property is currently
                        <strong>awaiting review</strong>
                        by the Flexy Properties team.
                    </p>

                    <p>
                        Please keep your submission reference
                        number. It will help us quickly identify
                        your property if you contact us.
                    </p>


                    <div style="
                        background:#fff8e7;
                        border:1px solid #f0dfae;
                        border-radius:8px;
                        padding:15px;
                        margin-top:25px;
                        color:#745c1f;
                        font-size:13px;
                    ">
                        <strong>Important:</strong>
                        Submission does not mean your property
                        has automatically been approved or
                        published. Our team will review the
                        information provided first.
                    </div>


                    <p style="margin-top:28px;">
                        Our team may contact you if additional
                        information or verification is required.
                    </p>

                    <p>
                        Thank you for choosing
                        <strong>Flexy Properties</strong>.
                    </p>

                </div>


                <div style="
                    background:#f5f7fa;
                    padding:20px;
                    text-align:center;
                    color:#7b8794;
                    font-size:12px;
                ">
                    Flexy Properties<br>
                    Property Marketplace
                </div>

            </div>

        </body>
        </html>
        """
        mail.send(msg)

    except Exception:
        current_app.logger.exception(
            "PROPERTY SUBMISSION CONFIRMATION EMAIL ERROR"
        )

def send_new_property_submission_admin_email(
    landlord_name,
    landlord_email,
    landlord_phone,
    property_title,
    property_type,
    listing_type,
    state,
    address,
    price,
    reference_number
):

    try:

        safe_name = escape(landlord_name)
        safe_email = escape(landlord_email)
        safe_phone = escape(landlord_phone)
        safe_title = escape(property_title)
        safe_type = escape(property_type)
        listing_label = {
            "SALE": "For Sale",
            "RENT": "For Rent"
        }.get(
            str(listing_type).lower(),
            str(listing_type).title()
        )
        safe_listing = escape(listing_label)
        safe_state = escape(state)
        safe_address = escape(address)
        safe_reference = escape(reference_number)

        formatted_price = (
            f"₦{price:,.2f}"
            if price is not None
            else "Not specified"
        )

        safe_price = escape(formatted_price)

        msg = Message(
            subject=(
                f"New Property Submission - "
                f"{reference_number}"
            ),
            recipients=[
                current_app.config["FLEXY_EMAIL"]
            ],
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            reply_to=str(landlord_email).strip()
        )

        msg.body = f"""

        New Property Submission

Reference:
{reference_number}

LANDLORD

Name:
{landlord_name}

Email:
{landlord_email}

Phone / WhatsApp:
{landlord_phone}


PROPERTY

Title:
{property_title}

Type:
{property_type}

Listing Type:
{listing_type}

State:
{state}

Address:
{address}

Price:
{formatted_price}


ACTION REQUIRED

Sign in to the Flexy Properties administration panel
to review this property submission.

Flexy Properties
"""

        # ==========================
        # HTML
        # ==========================

        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <body style="
            margin:0;
            padding:0;
            background:#f5f7fa;
            font-family:Arial,Helvetica,sans-serif;
        ">

            <div style="
                max-width:650px;
                margin:30px auto;
                background:#ffffff;
                border-radius:12px;
                overflow:hidden;
                border:1px solid #e3e8ee;
            ">

                <div style="
                    background:#0b1f33;
                    padding:30px;
                    color:#ffffff;
                ">

                    <div style="
                        color:#8ee0b3;
                        font-size:12px;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:1px;
                    ">
                        Administration Notification
                    </div>

                    <h2 style="
                        margin:8px 0 0;
                        font-size:22px;
                    ">
                        New Property Submission
                    </h2>

                </div>


                <div style="
                    padding:32px;
                    color:#374151;
                    line-height:1.6;
                ">

                    <div style="
                        background:#f1f7f4;
                        border:1px solid #d7eadf;
                        padding:16px;
                        border-radius:9px;
                        margin-bottom:25px;
                    ">

                        <div style="
                            font-size:11px;
                            color:#6b7280;
                            text-transform:uppercase;
                        ">
                            Submission Reference
                        </div>

                        <div style="
                            color:#198754;
                            font-size:20px;
                            font-weight:700;
                            margin-top:4px;
                        ">
                            {safe_reference}
                        </div>

                    </div>


                    <h3 style="
                        color:#0b1f33;
                        font-size:16px;
                        border-bottom:1px solid #e5e7eb;
                        padding-bottom:9px;
                    ">
                        Landlord Information
                    </h3>

                    <p>
                        <strong>Name:</strong>
                        {safe_name}
                    </p>

                    <p>
                        <strong>Email:</strong>
                        {safe_email}
                    </p>

                    <p>
                        <strong>Phone / WhatsApp:</strong>
                        {safe_phone}
                    </p>


                    <h3 style="
                        color:#0b1f33;
                        font-size:16px;
                        border-bottom:1px solid #e5e7eb;
                        padding-bottom:9px;
                        margin-top:28px;
                    ">
                        Property Information
                    </h3>

                    <p>
                        <strong>Title:</strong>
                        {safe_title}
                    </p>

                    <p>
                        <strong>Type:</strong>
                        {safe_type}
                    </p>
                    <p>
                        <strong>Listing Type:</strong>
                        {safe_listing}
                    </p>
                    <p>
                        <strong>State:</strong>
                        {safe_state}
                    </p>

                    <p>
                        <strong>Address:</strong>
                        {safe_address}
                    </p>

                    <p>
                        <strong>Asking Price:</strong>
                        {safe_price}
                    </p>


                    <div style="
                        background:#f8fafb;
                        border-left:4px solid #198754;
                        padding:16px;
                        margin-top:28px;
                        font-size:13px;
                    ">
                        <strong>Action required:</strong><br>
                        Sign in to the Flexy Properties
                        administration panel to review the
                        property information and uploaded images.
                    </div>

                </div>


                <div style="
                    background:#f5f7fa;
                    padding:18px;
                    text-align:center;
                    color:#7b8794;
                    font-size:12px;
                ">
                    Flexy Properties Administration
                </div>

            </div>

        </body>
        </html>
        """

        mail.send(msg)

    except Exception:
        current_app.logger.exception(
            "NEW PROPERTY SUBMISSION ADMIN EMAIL ERROR"
        )

def send_property_submission_approved_email(
    email,
    landlord_name,
    property_title,
    listing_type,
    reference_number
):

    try:

        recipient_email = str(email).strip()
        safe_name = escape(str(landlord_name))
        safe_title = escape(str(property_title))
        listing_label ={
            "sale": "For Sale",
            "rent": "For Rent",
        }.get(
            str(listing_type).lower(),
            str(listing_type).title()
        )

        safe_listing_type = escape(listing_label)

        safe_reference = escape(reference_number)
        whatsapp_message = quote(
                   f"Hello Flexy Properties, "
                   f"I am contacting you about my approved property "
                   f"submission {reference_number}."
               )
       
        whatsapp_url = (
            "https://wa.me/2349017096022"
            f"?text={whatsapp_message}"
        )

        msg = Message(
            subject=(
                f"Property Approved - "
                f"{reference_number}"
            ),
            recipients=[recipient_email],
            sender=current_app.config["MAIL_DEFAULT_SENDER"]
            
        )

        msg.body = f"""

        Hello {landlord_name},

Good news! Your property submission has been approved by Flexy Properties.

Submission Reference: {reference_number}
Property: {property_title}
Listing Purpose: {listing_label}

Your property has now been approved for publication on Flexy Properties.

Our team may contact you if any additional information is required regarding the listing or enquiries from interested property seekers.

Thank you for choosing Flexy Properties to market your property.

Flexy Properties
www.flexyproperties.org
"""


        msg.html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

</head>


<body
    style="
        margin:0;
        padding:0;
        background:#f2f4f7;
        font-family:Arial,Helvetica,sans-serif;
        color:#344054;
    "
>


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        background:#f2f4f7;
        padding:32px 15px;
    "
>

<tr>

<td align="center">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:600px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        box-shadow:
            0 4px 14px
            rgba(16,24,40,.08);
    "
>


    <!-- HEADER -->

    <tr>

        <td
            style="
                background:#101828;
                padding:25px 30px;
                text-align:center;
            "
        >

            <div
                style="
                    color:#ffffff;
                    font-size:22px;
                    font-weight:700;
                "
            >
                Flexy Properties
            </div>

            <div
                style="
                    color:#98a2b3;
                    font-size:12px;
                    margin-top:5px;
                "
            >
                Property Marketing & Marketplace
            </div>

        </td>

    </tr>



    <!-- CONTENT -->

    <tr>

        <td
            style="
                padding:35px 30px;
            "
        >


            <div
                style="
                    width:55px;
                    height:55px;
                    line-height:55px;
                    margin:0 auto 20px;
                    background:#ecfdf3;
                    border-radius:50%;
                    text-align:center;
                    color:#079455;
                    font-size:26px;
                    font-weight:bold;
                "
            >
                ✓
            </div>


            <h2
                style="
                    margin:0 0 10px;
                    text-align:center;
                    color:#101828;
                    font-size:22px;
                "
            >
                Property Approved
            </h2>


            <p
                style="
                    margin:0 0 28px;
                    text-align:center;
                    color:#667085;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Good news! Your property submission
                has been reviewed and approved by
                Flexy Properties.
            </p>


            <p
                style="
                    margin:0 0 20px;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Hello <strong>{safe_name}</strong>,
            </p>


            <p
                style="
                    margin:0 0 22px;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Your property has successfully passed
                our review and has been approved for
                publication on Flexy Properties.
            </p>



            <!-- PROPERTY DETAILS -->

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                style="
                    background:#f9fafb;
                    border:1px solid #eaecf0;
                    border-radius:10px;
                    margin-bottom:25px;
                "
            >

                <tr>

                    <td
                        style="
                            padding:18px;
                        "
                    >


                        <div
                            style="
                                margin-bottom:14px;
                            "
                        >

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Submission Reference
                            </div>

                            <div
                                style="
                                    color:#079455;
                                    font-size:15px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_reference}
                            </div>

                        </div>


                        <div
                            style="
                                margin-bottom:14px;
                            "
                        >

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Property
                            </div>

                            <div
                                style="
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_title}
                            </div>

                        </div>


                        <div>

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Listing Purpose
                            </div>

                            <div
                                style="
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_listing_type}
                            </div>

                        </div>


                    </td>

                </tr>

            </table>



            <div
                style="
                    padding:15px 17px;
                    background:#ecfdf3;
                    border-left:4px solid #079455;
                    border-radius:7px;
                    margin-bottom:25px;
                "
            >

                <strong
                    style="
                        display:block;
                        color:#067647;
                        font-size:13px;
                        margin-bottom:5px;
                    "
                >
                    Your property is now approved.
                </strong>


                <span
                    style="
                        color:#475467;
                        font-size:13px;
                        line-height:1.6;
                    "
                >
                    Flexy Properties may contact you
                    regarding enquiries from interested
                    property seekers or if additional
                    information is required.
                </span>

            </div>



            <p
                style="
                    margin:0;
                    color:#667085;
                    font-size:13px;
                    line-height:1.7;
                "
            >
                Thank you for choosing Flexy Properties
                to market your property.
            </p>


        </td>

    </tr>
    <!-- WHATSAPP CONTACT -->

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        margin-bottom:25px;
    "
>

    <tr>

        <td align="center">

            <a
                href="{whatsapp_url}"
                target="_blank"
                style="
                    display:inline-block;
                    background:#079455;
                    color:#ffffff;
                    text-decoration:none;
                    padding:13px 22px;
                    border-radius:8px;
                    font-size:13px;
                    font-weight:bold;
                "
            >
                Contact Flexy Properties on WhatsApp
            </a>

        </td>

    </tr>

    </table>



    <!-- FOOTER -->

    <tr>

        <td
            style="
                background:#f9fafb;
                border-top:1px solid #eaecf0;
                padding:20px 30px;
                text-align:center;
            "
        >

            <div
                style="
                    color:#667085;
                    font-size:12px;
                    line-height:1.6;
                "
            >
                Flexy Properties
                <br>
                Property Marketplace
            </div>


            <div
                style="
                    margin-top:7px;
                    color:#98a2b3;
                    font-size:11px;
                "
            >
                www.flexyproperties.org
            </div>

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
        return True
    except Exception:
        current_app.logger.exception(
            "PROPERTY SUBMISSION APPROVAL "
            "EMAIL ERROR"
        )

        return False



def send_property_submission_rejected_email(
    email,
    landlord_name,
    property_title,
    listing_type,
    reference_number,
    rejection_reason
):
    """
    Notify a landlord that their property submission
    was not approved.
    """

    try:

        recipient_email = str(email).strip()

        safe_name = escape(
            str(landlord_name)
        )

        safe_title = escape(
            str(property_title)
        )

        safe_reference = escape(
            str(reference_number)
        )

        safe_reason = escape(
            str(rejection_reason)
        )


        listing_label = {
            "sale": "For Sale",
            "rent": "For Rent"
        }.get(
            str(listing_type).lower(),
            str(listing_type).title()
        )

        safe_listing_type = escape(
            listing_label
        )
        whatsapp_message = quote(
            f"Hello Flexy Properties, "
            f"I am contacting you regarding my property "
            f"submission {reference_number}, which was not approved. "
            f"I would like some clarification."
        )

        whatsapp_url = (
            "https://wa.me/2349017096022"
            f"?text={whatsapp_message}"
        )

        msg = Message(
            subject=(
                f"Property Submission Review - "
                f"{reference_number}"
            ),
            recipients=[
                recipient_email
            ],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )


        msg.body = f"""
Hello {landlord_name},

We have completed the review of your property submission.

Submission Reference: {reference_number}
Property: {property_title}
Listing Purpose: {listing_label}

Unfortunately, the property submission was not approved for publication at this time.

Reason:
{rejection_reason}

If you believe the issue can be corrected or you need clarification, please contact Flexy Properties.

Thank you for your interest in marketing your property with us.

Flexy Properties
www.flexyproperties.org
"""


        msg.html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

</head>


<body
    style="
        margin:0;
        padding:0;
        background:#f2f4f7;
        font-family:Arial,Helvetica,sans-serif;
        color:#344054;
    "
>


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        background:#f2f4f7;
        padding:32px 15px;
    "
>

<tr>

<td align="center">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:600px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        box-shadow:
            0 4px 14px
            rgba(16,24,40,.08);
    "
>


    <!-- HEADER -->

    <tr>

        <td
            style="
                background:#101828;
                padding:25px 30px;
                text-align:center;
            "
        >

            <div
                style="
                    color:#ffffff;
                    font-size:22px;
                    font-weight:700;
                "
            >
                Flexy Properties
            </div>

            <div
                style="
                    color:#98a2b3;
                    font-size:12px;
                    margin-top:5px;
                "
            >
                Property Marketing & Marketplace
            </div>

        </td>

    </tr>



    <!-- CONTENT -->

    <tr>

        <td
            style="
                padding:35px 30px;
            "
        >


            <div
                style="
                    width:55px;
                    height:55px;
                    line-height:55px;
                    margin:0 auto 20px;
                    background:#fef3f2;
                    border-radius:50%;
                    text-align:center;
                    color:#d92d20;
                    font-size:25px;
                    font-weight:bold;
                "
            >
                ×
            </div>


            <h2
                style="
                    margin:0 0 10px;
                    text-align:center;
                    color:#101828;
                    font-size:22px;
                "
            >
                Property Submission Reviewed
            </h2>


            <p
                style="
                    margin:0 0 28px;
                    text-align:center;
                    color:#667085;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                We have completed the review of
                your property submission.
            </p>


            <p
                style="
                    margin:0 0 20px;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Hello <strong>{safe_name}</strong>,
            </p>


            <p
                style="
                    margin:0 0 22px;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Unfortunately, your property submission
                was not approved for publication on
                Flexy Properties at this time.
            </p>



            <!-- DETAILS -->

            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                style="
                    background:#f9fafb;
                    border:1px solid #eaecf0;
                    border-radius:10px;
                    margin-bottom:22px;
                "
            >

                <tr>

                    <td style="padding:18px;">


                        <div style="margin-bottom:14px;">

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Submission Reference
                            </div>

                            <div
                                style="
                                    color:#344054;
                                    font-size:15px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_reference}
                            </div>

                        </div>



                        <div style="margin-bottom:14px;">

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Property
                            </div>

                            <div
                                style="
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_title}
                            </div>

                        </div>



                        <div>

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Listing Purpose
                            </div>

                            <div
                                style="
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                    margin-top:4px;
                                "
                            >
                                {safe_listing_type}
                            </div>

                        </div>


                    </td>

                </tr>

            </table>



            <!-- REASON -->

            <div
                style="
                    padding:16px 18px;
                    background:#fef3f2;
                    border-left:4px solid #f04438;
                    border-radius:7px;
                    margin-bottom:24px;
                "
            >

                <div
                    style="
                        color:#b42318;
                        font-size:12px;
                        font-weight:bold;
                        text-transform:uppercase;
                        margin-bottom:7px;
                    "
                >
                    Reason for Rejection
                </div>


                <div
                    style="
                        color:#475467;
                        font-size:13px;
                        line-height:1.7;
                    "
                >
                    {safe_reason}
                </div>

            </div>



            <p
                style="
                    margin:0 0 14px;
                    color:#667085;
                    font-size:13px;
                    line-height:1.7;
                "
            >
                If the issue can be corrected or you
                require clarification, please contact
                Flexy Properties.
            </p>


            <p
                style="
                    margin:0;
                    color:#667085;
                    font-size:13px;
                    line-height:1.7;
                "
            >
                Thank you for your interest in marketing
                your property with us.
            </p>


        </td>

    </tr>

    <!-- WHATSAPP CONTACT -->

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        margin-bottom:25px;
    "
>

    <tr>

        <td align="center">

            <a
                href="{whatsapp_url}"
                target="_blank"
                style="
                    display:inline-block;
                    background:#079455;
                    color:#ffffff;
                    text-decoration:none;
                    padding:13px 22px;
                    border-radius:8px;
                    font-size:13px;
                    font-weight:bold;
                "
            >
                Contact Flexy Properties on WhatsApp
            </a>

        </td>

    </tr>

</table>



    <!-- FOOTER -->

    <tr>

        <td
            style="
                background:#f9fafb;
                border-top:1px solid #eaecf0;
                padding:20px 30px;
                text-align:center;
            "
        >

            <div
                style="
                    color:#667085;
                    font-size:12px;
                    line-height:1.6;
                "
            >
                Flexy Properties
                <br>
                Property Marketplace
            </div>


            <div
                style="
                    margin-top:7px;
                    color:#98a2b3;
                    font-size:11px;
                "
            >
                www.flexyproperties.org
            </div>

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

        return True


    except Exception:

        current_app.logger.exception(
            "PROPERTY SUBMISSION REJECTION "
            "EMAIL ERROR"
        )

        return False


from flask import current_app
from flask_mail import Message
from markupsafe import escape
from urllib.parse import quote

from pkg.extension import mail


def send_property_archived_email(
    email,
    landlord_name,
    property_title,
    listing_type,
    reference_number,
    archive_reason,
    archive_note=None
):

    try:

        recipient_email = str(email).strip()

        safe_name = escape(
            str(landlord_name)
        )

        safe_title = escape(
            str(property_title)
        )

        safe_reference = escape(
            str(reference_number)
        )


        listing_label = {
            "sale": "For Sale",
            "rent": "For Rent"
        }.get(
            str(listing_type).lower(),
            str(listing_type).title()
        )


        reason_label = {
            "landlord_withdrew":
                "Landlord Withdrew Property",

            "sold_elsewhere":
                "Sold Elsewhere",

            "rented_elsewhere":
                "Rented Elsewhere",

            "duplicate":
                "Duplicate Listing",

            "listing_error":
                "Listing Information Incorrect",

            "admin_removed":
                "Removed by Administrator",

            "other":
                "Other"
        }.get(
            archive_reason,
            "Property Archived"
        )


        safe_listing = escape(
            listing_label
        )

        safe_reason = escape(
            reason_label
        )

        safe_note = (
            escape(str(archive_note))
            if archive_note
            else None
        )


        whatsapp_message = quote(
            f"Hello Flexy Properties, "
            f"I am contacting you about my archived "
            f"property listing {reference_number}."
        )


        whatsapp_url = (
            "https://wa.me/2349017096022"
            f"?text={whatsapp_message}"
        )


        msg = Message(
            subject=(
                f"Property Listing Archived - "
                f"{reference_number}"
            ),
            recipients=[
                recipient_email
            ],
            sender=current_app.config[
                "MAIL_DEFAULT_SENDER"
            ]
        )


        msg.body = f"""
Hello {landlord_name},

Your property listing has been archived on Flexy Properties.

Submission Reference: {reference_number}
Property: {property_title}
Listing Purpose: {listing_label}
Archive Reason: {reason_label}

{f"Additional Information: {archive_note}" if archive_note else ""}

The property is no longer displayed as an active property on Flexy Properties.

Your original property submission and listing history remain securely recorded in our system.

If you have questions about this change, please contact Flexy Properties.

Flexy Properties
www.flexyproperties.org
"""


        note_html = ""

        if safe_note:

            note_html = f"""
            <div
                style="
                    margin-top:12px;
                    padding-top:12px;
                    border-top:1px solid #fedf89;
                "
            >

                <strong
                    style="
                        display:block;
                        margin-bottom:5px;
                        color:#93370d;
                        font-size:12px;
                    "
                >
                    Additional Information
                </strong>

                <span
                    style="
                        color:#475467;
                        font-size:13px;
                        line-height:1.6;
                    "
                >
                    {safe_note}
                </span>

            </div>
            """


        msg.html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

</head>


<body
    style="
        margin:0;
        padding:0;
        background:#f2f4f7;
        font-family:Arial,Helvetica,sans-serif;
        color:#344054;
    "
>


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        padding:32px 15px;
        background:#f2f4f7;
    "
>

<tr>

<td align="center">


<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:600px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        box-shadow:
            0 4px 14px
            rgba(16,24,40,.08);
    "
>


    <tr>

        <td
            style="
                padding:25px 30px;
                background:#101828;
                text-align:center;
            "
        >

            <div
                style="
                    color:#ffffff;
                    font-size:22px;
                    font-weight:bold;
                "
            >
                Flexy Properties
            </div>

            <div
                style="
                    margin-top:5px;
                    color:#98a2b3;
                    font-size:12px;
                "
            >
                Property Marketing & Marketplace
            </div>

        </td>

    </tr>


    <tr>

        <td style="padding:35px 30px;">


            <div
                style="
                    width:55px;
                    height:55px;
                    line-height:55px;
                    margin:0 auto 20px;
                    background:#fff7ed;
                    border-radius:50%;
                    text-align:center;
                    color:#c2410c;
                    font-size:23px;
                "
            >
                &#128230;
            </div>


            <h2
                style="
                    margin:0 0 10px;
                    color:#101828;
                    font-size:21px;
                    text-align:center;
                "
            >
                Property Listing Archived
            </h2>


            <p
                style="
                    margin:0 0 28px;
                    color:#667085;
                    font-size:14px;
                    line-height:1.7;
                    text-align:center;
                "
            >
                Your property is no longer displayed
                as an active listing on Flexy Properties.
            </p>


            <p
                style="
                    margin:0 0 20px;
                    font-size:14px;
                "
            >
                Hello <strong>{safe_name}</strong>,
            </p>


            <p
                style="
                    margin:0 0 23px;
                    color:#475467;
                    font-size:14px;
                    line-height:1.7;
                "
            >
                Your property listing has been archived.
                The original submission and listing
                history remain recorded in our system.
            </p>


            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                border="0"
                style="
                    margin-bottom:23px;
                    background:#f9fafb;
                    border:1px solid #eaecf0;
                    border-radius:10px;
                "
            >

                <tr>

                    <td style="padding:18px;">


                        <div style="margin-bottom:14px;">

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Submission Reference
                            </div>

                            <div
                                style="
                                    margin-top:4px;
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                "
                            >
                                {safe_reference}
                            </div>

                        </div>


                        <div style="margin-bottom:14px;">

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Property
                            </div>

                            <div
                                style="
                                    margin-top:4px;
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                "
                            >
                                {safe_title}
                            </div>

                        </div>


                        <div>

                            <div
                                style="
                                    color:#98a2b3;
                                    font-size:11px;
                                    font-weight:bold;
                                    text-transform:uppercase;
                                "
                            >
                                Listing Purpose
                            </div>

                            <div
                                style="
                                    margin-top:4px;
                                    color:#344054;
                                    font-size:14px;
                                    font-weight:bold;
                                "
                            >
                                {safe_listing}
                            </div>

                        </div>


                    </td>

                </tr>

            </table>


            <div
                style="
                    margin-bottom:25px;
                    padding:16px 18px;
                    background:#fffaeb;
                    border-left:4px solid #f79009;
                    border-radius:7px;
                "
            >

                <div
                    style="
                        margin-bottom:6px;
                        color:#93370d;
                        font-size:11px;
                        font-weight:bold;
                        text-transform:uppercase;
                    "
                >
                    Archive Reason
                </div>


                <div
                    style="
                        color:#344054;
                        font-size:14px;
                        font-weight:bold;
                    "
                >
                    {safe_reason}
                </div>


                {note_html}

            </div>


            <p
                style="
                    margin:0 0 18px;
                    color:#667085;
                    font-size:13px;
                    line-height:1.7;
                "
            >
                If you have questions about this
                change, you can contact Flexy Properties
                directly on WhatsApp.
            </p>


            <table
                width="100%"
                cellpadding="0"
                cellspacing="0"
                border="0"
            >

                <tr>

                    <td align="center">

                        <a
                            href="{whatsapp_url}"
                            target="_blank"
                            style="
                                display:inline-block;
                                padding:13px 22px;
                                background:#079455;
                                border-radius:8px;
                                color:#ffffff;
                                font-size:13px;
                                font-weight:bold;
                                text-decoration:none;
                            "
                        >
                            Contact Flexy Properties
                            on WhatsApp
                        </a>

                    </td>

                </tr>

            </table>


        </td>

    </tr>


    <tr>

        <td
            style="
                padding:20px 30px;
                background:#f9fafb;
                border-top:1px solid #eaecf0;
                text-align:center;
            "
        >

            <div
                style="
                    color:#667085;
                    font-size:12px;
                "
            >
                Flexy Properties
            </div>

            <div
                style="
                    margin-top:5px;
                    color:#98a2b3;
                    font-size:11px;
                "
            >
                www.flexyproperties.org
            </div>

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

        return True


    except Exception:

        current_app.logger.exception(
            "PROPERTY ARCHIVED EMAIL ERROR"
        )

        return False