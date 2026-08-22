export default function EmptyState({ icon: Icon, title, description }) {
    return (
        <div className="text-center py-12">
            {Icon && <Icon className="mx-auto text-slate-300 mb-3" size={40} />}
            <p className="text-slate-600 font-medium">{title}</p>
            {description && <p className="text-slate-400 text-sm mt-1">{description}</p>}
        </div>
    );
}