"""
メール送信ユーティリティ
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import os


def send_appointment_approval_email(
    to_email: str,
    client_name: str,
    coach_name: str,
    appointment_date: str,
    meeting_url: str,
    notes: Optional[str] = None
) -> bool:
    """
    面談承認メールを送信

    Args:
        to_email: 送信先メールアドレス
        client_name: 利用者名
        coach_name: コーチ名
        appointment_date: 面談日時
        meeting_url: オンライン面談URL
        notes: 備考

    Returns:
        bool: 送信成功時True、失敗時False
    """
    # 環境変数からSMTP設定を取得
    smtp_host = os.getenv('SMTP_HOST', 'localhost')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # メール本文を作成
    subject = f"【面談承認】{appointment_date}の面談が承認されました"

    body = f"""
{client_name} 様

いつもお世話になっております。

{appointment_date}の面談リクエストが承認されました。

■面談詳細
担当コーチ: {coach_name}
日時: {appointment_date}
面談URL: {meeting_url}
"""

    if notes:
        body += f"\n備考: {notes}\n"

    body += """

上記URLにアクセスして、面談にご参加ください。

よろしくお願いいたします。

---
medcareercoach
"""

    try:
        # MIMEオブジェクトを作成
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # 本文を追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTPサーバーに接続してメール送信（本番環境のみ）
        if smtp_host != 'localhost' and smtp_user and smtp_password:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"メール送信成功: {to_email}")
            return True
        else:
            # 開発環境では送信をスキップしてログ出力のみ
            print(f"[開発環境] メール送信スキップ: {to_email}")
            print(f"件名: {subject}")
            print(f"本文:\n{body}")
            return True

    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def send_appointment_approval_email_multi(
    to_email: str,
    client_name: str,
    coach_names: List[str],
    appointment_date: str,
    meeting_url: str,
    notes: Optional[str] = None,
    is_for_coach: bool = False
) -> bool:
    """
    面談承認メールを送信（複数コーチ対応）

    Args:
        to_email: 送信先メールアドレス
        client_name: 利用者名
        coach_names: コーチ名のリスト
        appointment_date: 面談日時
        meeting_url: オンライン面談URL
        notes: 備考
        is_for_coach: コーチ宛てのメールかどうか

    Returns:
        bool: 送信成功時True、失敗時False
    """
    # 環境変数からSMTP設定を取得
    smtp_host = os.getenv('SMTP_HOST', 'localhost')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # メール本文を作成
    coach_names_str = '、'.join(coach_names)

    if is_for_coach:
        # コーチ宛て
        subject = f"【面談確定】{client_name}様の面談が確定しました"
        body = f"""
{to_email} 様

いつもお世話になっております。

{client_name}様の面談リクエストを承認しました。

■面談詳細
利用者: {client_name}
担当コーチ: {coach_names_str}
日時: {appointment_date}
面談URL: {meeting_url}
"""
    else:
        # 利用者宛て
        subject = f"【面談承認】{appointment_date}の面談が承認されました"
        body = f"""
{client_name} 様

いつもお世話になっております。

{appointment_date}の面談リクエストが承認されました。

■面談詳細
担当コーチ: {coach_names_str}
日時: {appointment_date}
面談URL: {meeting_url}
"""

    if notes:
        body += f"\n備考: {notes}\n"

    body += """

上記URLにアクセスして、面談にご参加ください。

よろしくお願いいたします。

---
medcareercoach
"""

    try:
        # MIMEオブジェクトを作成
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # 本文を追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTPサーバーに接続してメール送信（本番環境のみ）
        if smtp_host != 'localhost' and smtp_user and smtp_password:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"メール送信成功: {to_email}")
            return True
        else:
            # 開発環境では送信をスキップしてログ出力のみ
            print(f"[開発環境] メール送信スキップ: {to_email}")
            print(f"件名: {subject}")
            print(f"本文:\n{body}")
            return True

    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def send_appointment_cancellation_email(
    to_email: str,
    client_name: str,
    coach_names: List[str],
    appointment_date: str,
    cancellation_reason: Optional[str] = None,
    is_for_coach: bool = False
) -> bool:
    """
    面談キャンセルメールを送信（複数コーチ対応）

    Args:
        to_email: 送信先メールアドレス
        client_name: 利用者名
        coach_names: コーチ名のリスト
        appointment_date: 面談日時
        cancellation_reason: キャンセル理由
        is_for_coach: コーチ宛てのメールかどうか

    Returns:
        bool: 送信成功時True、失敗時False
    """
    # 環境変数からSMTP設定を取得
    smtp_host = os.getenv('SMTP_HOST', 'localhost')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # メール本文を作成
    coach_names_str = '、'.join(coach_names)

    if is_for_coach:
        # コーチ宛て
        subject = f"【面談キャンセル】{client_name}様の面談がキャンセルされました"
        body = f"""
{to_email} 様

いつもお世話になっております。

{client_name}様の面談がキャンセルされました。

■キャンセルされた面談
利用者: {client_name}
担当コーチ: {coach_names_str}
日時: {appointment_date}
"""
    else:
        # 利用者宛て
        subject = f"【面談キャンセル】{appointment_date}の面談がキャンセルされました"
        body = f"""
{client_name} 様

いつもお世話になっております。

{appointment_date}の面談がキャンセルされました。

■キャンセルされた面談
担当コーチ: {coach_names_str}
日時: {appointment_date}
"""

    if cancellation_reason:
        body += f"\nキャンセル理由: {cancellation_reason}\n"

    body += """

再度面談をご希望の際は、お手数ですが面談予約画面から新しい予約を作成してください。

よろしくお願いいたします。

---
medcareercoach
"""

    try:
        # MIMEオブジェクトを作成
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # 本文を追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTPサーバーに接続してメール送信（本番環境のみ）
        if smtp_host != 'localhost' and smtp_user and smtp_password:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"キャンセルメール送信成功: {to_email}")
            return True
        else:
            # 開発環境では送信をスキップしてログ出力のみ
            print(f"[開発環境] キャンセルメール送信スキップ: {to_email}")
            print(f"件名: {subject}")
            print(f"本文:\n{body}")
            return True

    except Exception as e:
        print(f"キャンセルメール送信エラー: {e}")
        return False


def send_appointment_update_email(
    to_email: str,
    client_name: str,
    coach_names: List[str],
    old_appointment_date: str,
    new_appointment_date: str,
    meeting_url: str,
    update_reason: Optional[str] = None,
    notes: Optional[str] = None,
    is_for_coach: bool = False
) -> bool:
    """
    面談変更メールを送信（複数コーチ対応）

    Args:
        to_email: 送信先メールアドレス
        client_name: 利用者名
        coach_names: コーチ名のリスト
        old_appointment_date: 変更前の面談日時
        new_appointment_date: 変更後の面談日時
        meeting_url: オンライン面談URL
        update_reason: 変更理由
        notes: 備考
        is_for_coach: コーチ宛てのメールかどうか

    Returns:
        bool: 送信成功時True、失敗時False
    """
    # 環境変数からSMTP設定を取得
    smtp_host = os.getenv('SMTP_HOST', 'localhost')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')

    # メール本文を作成
    coach_names_str = '、'.join(coach_names)

    if is_for_coach:
        # コーチ宛て
        subject = f"【面談変更】{client_name}様の面談日時が変更されました"
        body = f"""
{to_email} 様

いつもお世話になっております。

{client_name}様の面談日時が変更されました。

■変更前
日時: {old_appointment_date}

■変更後
利用者: {client_name}
担当コーチ: {coach_names_str}
日時: {new_appointment_date}
面談URL: {meeting_url}
"""
    else:
        # 利用者宛て
        subject = f"【面談変更】{old_appointment_date}の面談日時が変更されました"
        body = f"""
{client_name} 様

いつもお世話になっております。

{old_appointment_date}の面談日時が変更されました。

■変更前
日時: {old_appointment_date}

■変更後
担当コーチ: {coach_names_str}
日時: {new_appointment_date}
面談URL: {meeting_url}
"""

    if update_reason:
        body += f"\n変更理由: {update_reason}\n"

    if notes:
        body += f"\n備考: {notes}\n"

    body += """

上記URLにアクセスして、面談にご参加ください。

よろしくお願いいたします。

---
medcareercoach
"""

    try:
        # MIMEオブジェクトを作成
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # 本文を追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTPサーバーに接続してメール送信（本番環境のみ）
        if smtp_host != 'localhost' and smtp_user and smtp_password:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"変更メール送信成功: {to_email}")
            return True
        else:
            # 開発環境では送信をスキップしてログ出力のみ
            print(f"[開発環境] 変更メール送信スキップ: {to_email}")
            print(f"件名: {subject}")
            print(f"本文:\n{body}")
            return True

    except Exception as e:
        print(f"変更メール送信エラー: {e}")
        return False

