import React from 'react';

const TaskType = ({handleGetFilterTask}) => {
    const taskTypes = [
        {
            id: 1,
            name: 'Adliye İçi',
        },
        {
            id: 2,
            name: 'Adliye Dışı',
        },
    ];
    const handleSendFilter = (checked, id) => {
        if (checked) {
            handleGetFilterTask(id,"type",true)
        } else {
            handleGetFilterTask(id,"type",false)
        }
    }
    return (
        <>
            {taskTypes.map((currency) => (
                <li key={currency.id}>
                    <label className="flex items-center cursor-pointer w-full">
                        <input
                            type="checkbox"
                            id={currency.id}
                            name={currency.name}
                            value={currency.name}
                            onChange={(e) => {
                                handleSendFilter(e.target.checked, currency.id)
                            }}
                            className="h-5 w-5 mr-3 rounded border-jacarta-200 text-accent checked:bg-accent focus:ring-accent/20 focus:ring-offset-0 dark:border-jacarta-500 dark:bg-jacarta-600"
                        />
                        <span className="font-display text-sm font-semibold text-jacarta-700 dark:text-white">
						  {currency.name}
						</span>
                    </label>
                </li>
            ))}
        </>
    );
};

export default TaskType;
