import colorbrewer from 'colorbrewer';

const colorbrewerCategories = {
    sequential: ['Blues_9', 'BuGn_9', 'BuPu_9', 'GnBu_9', 'Greens_9', 'Greys_9', 'OrRd_9', 'Oranges_9', 'PuBu_9', 'PuBuGn_9', 'PuRd_9', 'Purples_9', 'RdPu_9', 'Reds_9', 'YlGn_9', 'YlGnBu_9', 'YlOrBr_9', 'YlOrRd_9'],
    diverging: ['BrBG_11', 'PRGn_11', 'PiYG_11', 'PuOr_11', 'RdBu_11', 'RdGy_11', 'RdYlBu_11', 'RdYlGn_11', 'Spectral_11'],
    qualitative: ['Accent_8', 'Dark2_8', 'Paired_12', 'Pastel1_9', 'Pastel2_8', 'Set1_9', 'Set2_8', 'Set3_12']
};

function toScheme(palettable) {
    if (!palettable) {
        return null;
    }
    return colorbrewer[palettable.split('.').slice(-1)[0].split('_')[0]];
}

function toSchemeColors(palettable) {
    if (!palettable) {
        return null;
    }
    var [scheme, number] = palettable.split('.').slice(-1)[0].split('_');
    return colorbrewer[scheme][number];
}

function toPalettable(schemeName) {
    if (!schemeName) {
        return null;
    }
    let out_category, out_scheme;
    for (let [category, scheme] of Object.entries(colorbrewerCategories)) {
        for (let schemeWithNumber of scheme) {
            if (schemeWithNumber === schemeName) {
                out_category = category;
                out_scheme = schemeWithNumber;
            }
        }
    }
    return `colorbrewer.${out_category}.${out_scheme}`;
}

export { colorbrewerCategories, toScheme, toSchemeColors, toPalettable };
