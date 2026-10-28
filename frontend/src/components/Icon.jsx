import React from 'react';

const paths={
 home:<><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/></>,
 book:<><path d="M12 6v15M3 3c4-1 6 0 9 3 3-3 5-4 9-3v15c-4-1-6 0-9 3-3-3-5-4-9-3Z"/></>,
 spark:<><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5ZM20 2v4M18 4h4"/></>,
 practice:<><path d="m14 3-3 7H4l7 4-2 7 11-12h-8l2-6Z"/></>,
 folder:<><path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z"/></>,
 history:<><path d="M3 11a9 9 0 1 1 2.5 7M3 4v7h7M12 7v5l3 2"/></>,
 send:<><path d="m21 3-7 18-4-8-8-4ZM21 3 10 13"/></>,
 plus:<><path d="M12 5v14M5 12h14"/></>,
 arrow:<><path d="m9 5 7 7-7 7"/></>,
 back:<><path d="m15 5-7 7 7 7"/></>,
 logout:<><path d="M9 4H4v16h5M14 8l4 4-4 4M8 12h12"/></>,
 menu:<><path d="M4 6h16M4 12h16M4 18h16"/></>,
 close:<><path d="m6 6 12 12M18 6 6 18"/></>,
 chat:<><path d="M21 11a9 9 0 0 1-9 9H4l-3 2 2-7a9 9 0 1 1 18-4Z"/></>,
 check:<><path d="m5 12 4 4L19 6"/></>,
 search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
 user:<><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></>,
 shield:<><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/></>,
 chevron:<><path d="m6 9 6 6 6-6"/></>,
 star:<><path d="m12 3 2.8 5.7 6.3.9-4.5 4.4 1.1 6.3-5.7-3-5.7 3 1.1-6.3L3 9.6l6.2-.9Z"/></>,
};
export default function Icon({name,size=20,...props}){
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name]||paths.book}</svg>;
}
