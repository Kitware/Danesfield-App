const mapping = [
    {
        "value": 0,
        "name": "Unclassified",
        "color": [
            0,
            0,
            0
        ]
    },
    {
        "value": 1,
        "name": "Asphalt",
        "color": [
            78,
            78,
            79
        ]
    },
    {
        "value": 2,
        "name": "Concrete/stone",
        "color": [
            161,
            161,
            163
        ]
    },
    {
        "value": 3,
        "name": "Glass",
        "color": [
            255,
            186,
            250
        ]
    },
    {
        "value": 4,
        "name": "Tree",
        "color": [
            16,
            119,
            14
        ]
    },
    {
        "value": 5,
        "name": "Non-tree vegetation",
        "color": [
            105,
            249,
            102
        ]
    },
    {
        "value": 6,
        "name": "Metal",
        "color": [
            240,
            252,
            103
        ]
    },
    {
        "value": 7,
        "name": "Red ceramic",
        "color": [
            214,
            0,
            60
        ]
    },
    {
        "value": 8,
        "name": "Soil",
        "color": [
            153,
            120,
            59
        ]
    },
    {
        "value": 9,
        "name": "Solar panel",
        "color": [
            179,
            74,
            239
        ]
    },
    {
        "value": 10,
        "name": "Water",
        "color": [
            124,
            161,
            255
        ]
    },
    {
        "value": 11,
        "name": "Polymer",
        "color": [
            255,
            255,
            255
        ]
    }
];

const palette = mapping.map((mapping) => {
    return '#' + mapping.color.map(number => number.toString(16).padStart(2, '0')).join('');
})

export {
    mapping,
    palette
}
