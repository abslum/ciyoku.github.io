function normalizeSize(size) {
    if (size === 'sm' || size === 'lg') return size;
    return 'md';
}

export function createIosLoader(options = {}) {
    const spinner = document.createElement('span');
    const size = normalizeSize(options.size);
    spinner.className = `ios-loader ios-loader-${size}`;
    if (options.accent === true) {
        spinner.classList.add('ios-loader-accent');
    }
    spinner.setAttribute('aria-hidden', 'true');
    return spinner;
}

export function createLoadingIndicator(options = {}) {
    const wrapper = document.createElement('div');
    wrapper.className = options.className || 'loading-indicator';
    wrapper.setAttribute('role', 'status');
    wrapper.setAttribute('aria-live', 'polite');
    wrapper.setAttribute('aria-label', options.ariaLabel || 'Loading');
    wrapper.appendChild(createIosLoader({
        size: options.size,
        accent: options.accent
    }));
    return wrapper;
}
