from kafka_client import send_view_event, send_click_event, send_like_event, send_comment_event

class PromocodeService:

    def view_promocode(self, user_id: int, promocode_id: int):
        # Логика просмотра промокода
        send_view_event(user_id, promocode_id)

    def click_promocode(self, user_id: int, promocode_id: int):
        # Логика клика по промокоду
        send_click_event(user_id, promocode_id)

    def like_promocode(self, user_id: int, promocode_id: int):
        # Логика лайка промокода
        send_like_event(user_id, promocode_id)

    def comment_promocode(self, user_id: int, promocode_id: int, comment: str):
        # Логика комментирования промокода
        send_comment_event(user_id, promocode_id, comment)
