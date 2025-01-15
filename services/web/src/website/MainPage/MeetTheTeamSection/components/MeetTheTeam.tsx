import HubberModule from './HubberModule';
import hubbers from '../StaticContent/hubbers.json';
import '@/components/EmblaCarousel/SlidesPerViewCarousel/css/base.css';
import '@/components/EmblaCarousel/SlidesPerViewCarousel/css/embla-team.css';
import EmblaCarousel from '@/components/EmblaCarousel/SlidesPerViewCarousel/js/EmblaCarousel.tsx';
import { EmblaOptionsType } from 'embla-carousel';
import React, { useState } from 'react';

// Because the grid for the meet the team secion is 2x4
// each slide of the carousel is going to be of 2 elements above each other
// chunkArray splits the array of members into an array where each element consists of another array of 2 members
// which is then passed in order for the 2x4 grid carousel logic to work

// TO-DO: make api call for the actual pictures and hubbers information

function chunkArray(array: React.ReactElement[], chunkSize: number): React.ReactElement[][] {
    return array.reduce((resultArray, item, index) => {
        const chunkIndex = Math.floor(index / chunkSize);
        if (!resultArray[chunkIndex]) {
            resultArray[chunkIndex] = []; // Start a new chunk
        }
        resultArray[chunkIndex].push(item);
        return resultArray;
    }, [] as React.ReactElement[][]);
}

const OPTIONS: EmblaOptionsType = {
    slidesToScroll: 'auto',
    containScroll: 'trimSnaps',
};

export default function PastEventSection() {
    const [selected, setSelected] = useState('All');
    console.log(OPTIONS);
    const handleSelect = (value: string) => {
    setSelected(value);
    };

    const initialSlides: React.ReactElement[] = hubbers
        .filter((hubbers) => hubbers.departments.includes(selected))
        .map((hubber, index) => <HubberModule imgSrc={hubber.picture} name={hubber.name} key={index} />);

    const SLIDES: React.ReactElement[][] = chunkArray(initialSlides, 2);

    return (
        <div className="space-y-7 font-mont sm:w-3/5 w-11/12 mx-auto">
            <h2 className="font-semibold text-3xl text-secondary text-[#9CBEFF] mb-10 ">Meet the team</h2>
            <div className="flex flex-wrap gap-3 ">
                {['All', 'Board', 'PR', 'Design', 'Development', 'Marketing', 'Logistics'].map((label) => (
                    <button
                        key={label}
                        className={`px-4 py-2 text-sm font-semibold rounded-2xl border focus:outline-none ${
                            selected === label ? 'bg-white text-blue-900' : 'text-gray-300 hover:white hover:text-white'
                        }`}
                        onClick={() => handleSelect(label)}
                    >
                        {label}
                    </button>
                ))}
            </div>
            <EmblaCarousel type="team" slides={SLIDES} options={OPTIONS} />
        </div>
    );
}
