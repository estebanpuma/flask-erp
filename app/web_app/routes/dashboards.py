from flask import Blueprint, render_template
import datetime

dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/')


MOTIVATIONAL_QUOTES = [
    "🎯 *Cada par de zapatos que hacemos lleva el orgullo de nuestro equipo.*",
    "🤝 *Una venta no es el final, es el inicio de una relación.*",
    "🛠️ *Si mejoras un 1% cada día, en un mes serás irreconocible.*",
    "🚀 *La excelencia no es un acto, es un hábito.*",
    "🎯 *Lo que no se mide, no se mejora. ¡Vamos por más!*",
    "🔧 *Los pequeños detalles hacen los grandes productos.*",
    "💡 *Una mente enfocada puede transformar toda una fábrica.*",
    "👟 *Hoy es un buen día para fabricar con propósito.*",
    "🏆 *Nuestro cliente final siente el esfuerzo que pusiste hoy.*",
    "📈 *Vender es ayudar: entendamos y resolvamos.*",
    "🌱 *Liderar es servir con visión.*",
    "🔁 *No hay errores, hay aprendizajes que optimizan.*"
]


def get_daily_quote():
    day_index = datetime.date.today().timetuple().tm_yday % len(MOTIVATIONAL_QUOTES)
    return MOTIVATIONAL_QUOTES[day_index]

@dashboards_bp.route('/')
def home():
    daily_quote = get_daily_quote()
    return render_template('dashboards/home.html', daily_quote = daily_quote)