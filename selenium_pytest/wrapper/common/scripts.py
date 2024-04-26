IS_ELEMENT_COMPLETELY_IN_VIEWPORT = """ var bounding = arguments[0].getBoundingClientRect();
    var viewportBottom = window.innerHeight || document.documentElement.clientHeight;
    var viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    return (
        bounding.top >= 0 &&
        bounding.left >= 0 &&
        bounding.bottom <= (viewportBottom) &&
        bounding.right <= (viewportWidth)
    )
"""

IS_ELEMENT_PARTIALLY_IN_VIEWPORT = """ var bounding = arguments[0].getBoundingClientRect();
    var viewportBottom = window.innerHeight || document.documentElement.clientHeight;
    var viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    return (
        (
            //top left corner in view
            bounding.top >= 0 && bounding.top < (viewportBottom) &&
            bounding.left >= 0 && bounding.left < (viewportWidth)
        )
        ||
        (   //top right corner in vew
            bounding.top >= 0 && bounding.top <= (viewportBottom) &&
            bounding.right > 0 && bounding.right <= (viewportWidth)
        )
        ||
        (   //bottom left corner in view
            bounding.bottom >= 0 && bounding.bottom <= (viewportBottom) &&
            bounding.left >= 0 && bounding.left <= (viewportWidth)
        )
        ||
        (   //bottom right corner in view
            bounding.bottom >= 0 && bounding.bottom <= (viewportBottom) &&
            bounding.right >= 0 && bounding.right <= (viewportWidth)
        )
    )
"""
