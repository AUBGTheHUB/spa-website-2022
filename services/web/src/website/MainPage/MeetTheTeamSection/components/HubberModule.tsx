type HubberModuleType = {
    imgSrc: string;
    name: string;
};

export default function HubberModule({ imgSrc, name }: HubberModuleType) {
    return (
        <div className="flex flex-col min-w-28 max-w-80 max-[450px]:max-w-full h-70 p-2 border rounded-2xl font-semibold">
            <div className="h-5/6 w-full">
                <img src={imgSrc} alt={name} className="object-cover w-full h-full rounded-xl" />
            </div>
            <div className="h-1/6 py-3 gap-2">
                <h3 className="text-secondary">{name}</h3>
            </div>
        </div>
    );
}
