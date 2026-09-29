const CARAS = {
  bien: '😄',
  alerta: '🙂',
  critico: '😬',
}

export default function AldoAvatar({ estado = 'bien', size = 'lg' }) {
  const dimensiones = size === 'lg' ? 'h-16 w-16 text-3xl' : 'h-10 w-10 text-xl'

  return (
    <div
      className={`flex ${dimensiones} shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-400 via-fuchsia-400 to-amber-300 shadow-lg shadow-fuchsia-200 dark:shadow-fuchsia-950`}
    >
      <span>{CARAS[estado] ?? CARAS.bien}</span>
    </div>
  )
}
