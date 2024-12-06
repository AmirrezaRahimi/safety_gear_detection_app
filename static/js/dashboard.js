class Dashboard {
    constructor() {
        this.elements = {
            peopleCount: document.getElementById('people-count'),
            hardhatCount: document.getElementById('hardhat-count'),
            vestCount: document.getElementById('vest-count'),
            maskCount: document.getElementById('mask-count')
        };
    }

    update(stats) {
        this.elements.peopleCount.innerText = stats.people || 0;
        this.elements.hardhatCount.innerText = stats['Hardhat'] || 0;
        this.elements.vestCount.innerText = stats['Safety Vest'] || 0;
        this.elements.maskCount.innerText = stats['Mask'] || 0;
    }
}
