import { Banknote, Car, HeartPulse, Home, Repeat, Zap } from 'lucide-react'

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
