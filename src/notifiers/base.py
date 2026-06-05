"""通知モジュールの抽象基底クラス"""
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """
    通知クラスの共通インターフェース。
    GmailNotifier / LineNotifier は このクラスを継承して実装する。
    """

    @abstractmethod
    def notify(self, items: list[dict]) -> None:
        """
        新着商品を通知する。

        Args:
            items: 通知する商品リスト
                   [{"brand", "name", "price", "url", "site"}, ...]
        """
        raise NotImplementedError
