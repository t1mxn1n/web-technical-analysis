from djongo import models


class FondsArray(models.Model):
    name = models.CharField(max_length=50, default='', verbose_name='Fond ticker', primary_key=True)
    added = models.CharField(max_length=50, default='by_admin')

    class Meta:
        verbose_name_plural = "Fonds tickers"

    def __str__(self):
        return f"{self.name}"


class CryptoArray(models.Model):
    name = models.CharField(max_length=50, default='', verbose_name='Crypto token', primary_key=True)
    added = models.CharField(max_length=50, default='by_admin')

    class Meta:
        verbose_name_plural = "Crypto tokens"

    def __str__(self):
        return f"{self.name}"
