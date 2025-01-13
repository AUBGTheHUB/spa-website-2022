import EventTicket from './EventTicket.tsx';
import pastEvents from '../StaticContent/pastEvents.json';
import '@/components/EmblaCarousel/SlidesPerViewCarousel/css/base.css';
import '@/components/EmblaCarousel/SlidesPerViewCarousel/css/embla.css';
import EmblaCarousel from '@/components/EmblaCarousel/SlidesPerViewCarousel/js/EmblaCarousel.tsx';
import { EmblaOptionsType } from 'embla-carousel';
import React from 'react';

const SLIDES: React.ReactElement[] = pastEvents.map((pastEvent, index) => (
    <EventTicket imgSrc={pastEvent.cover_picture} title={pastEvent.title} tags={pastEvent.tags} key={index} />
));

const OPTIONS: EmblaOptionsType = { align: 'start', slidesToScroll: 'auto' };

export default function PastEventSection() {
    return (
        <div className="space-y-7 font-mont">
            <h2 className="font-semibold text-3xl text-primary mb-10">Our Past Events</h2>
            <EmblaCarousel type="events" slides={SLIDES} options={OPTIONS} />
        </div>
    );
}
