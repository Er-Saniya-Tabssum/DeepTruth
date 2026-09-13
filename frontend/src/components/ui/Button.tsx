import React from 'react'

export function Button({children, className='', ...props}: any){
  return <button className={["px-4 py-2 rounded bg-blue-600 text-white", className].join(' ')} {...props}>{children}</button>
}
