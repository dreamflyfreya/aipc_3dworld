from .models import Product, CountrySpecificPrice, CountryEconomicIndicator

def calculate_price(product_id, country_code):
    product = Product.objects.get(id=product_id)
    try:
        country_price = product.prices.get(country_code=country_code.upper())
        return country_price.price
    except CountrySpecificPrice.DoesNotExist:
        # Fallback to adjusted price based on economic indicators
        try:
            indicator = CountryEconomicIndicator.objects.get(country=country_code.upper())
            # Example adjustment: baseline (US GDP per capita) / country GDP per capita
            adjustment_factor = 76329.6 / indicator.ppp_gdp_per_capita
            adjusted_price = product.default_price * adjustment_factor
            return adjusted_price
        except CountryEconomicIndicator.DoesNotExist:
            return product.default_price
