import { Banknote, Beer, Bus, Car, Croissant, HeartPulse, Home, Repeat, ShoppingCart, UtensilsCrossed, Zap } from 'lucide-react'

export const CATEGORIAS = ['Alquiler', 'Servicios', 'Suscripciones', 'Transporte', 'Salud', 'Otros']

export const ICONO_CATEGORIA = {
  Alquiler: Home,
  Servicios: Zap,
  Suscripciones: Repeat,
  Transporte: Car,
  Salud: HeartPulse,
  Otros: Banknote,
}

// Orden fijo tomado de la paleta categórica validada (dataviz skill) — nunca reordenar
// por valor/ranking, la seguridad ante daltonismo depende de este orden.
export const COLOR_CATEGORIA = {
  Alquiler: '#2a78d6',
  Servicios: '#1baf7a',
  Suscripciones: '#eda100',
  Transporte: '#008300',
  Salud: '#4a3aa7',
  Otros: '#e34948',
}

// Categorías de los gastos del día. Tienen que coincidir con CATEGORIAS_GASTO del backend.
export const CATEGORIAS_GASTO = ['Súper', 'Panadería', 'Comida afuera', 'Transporte', 'Salidas', 'Otros']

export const ICONO_CATEGORIA_GASTO = {
  Súper: ShoppingCart,
  Panadería: Croissant,
  'Comida afuera': UtensilsCrossed,
  Transporte: Bus,
  Salidas: Beer,
  Otros: Banknote,
}
