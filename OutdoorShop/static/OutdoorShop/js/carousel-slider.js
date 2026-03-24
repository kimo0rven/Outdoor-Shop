document.addEventListener('DOMContentLoaded', function() {
    const track = document.getElementById('carouselTrack');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const originalCards = Array.from(track.children);
    
    if (originalCards.length === 0) return;

    const clonesNeeded = 7; 
    let index = clonesNeeded;
    let isTransitioning = false;

    function getCardWidth() {
        return originalCards[0].getBoundingClientRect().width + 20;
    }

    for (let i = 0; i < clonesNeeded; i++) {
        let cloneIndex = (originalCards.length - 1) - (i % originalCards.length);
        let clone = originalCards[cloneIndex].cloneNode(true);
        track.insertBefore(clone, track.firstChild);
    }

    for (let i = 0; i < clonesNeeded; i++) {
        let cloneIndex = i % originalCards.length;
        let clone = originalCards[cloneIndex].cloneNode(true);
        track.appendChild(clone);
    }

    const allCards = Array.from(track.children);
    track.style.transform = `translateX(-${index * getCardWidth()}px)`;

    nextBtn.addEventListener('click', () => {
        if (isTransitioning) return;
        isTransitioning = true;
        index++;
        track.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        track.style.transform = `translateX(-${index * getCardWidth()}px)`;
    });

    prevBtn.addEventListener('click', () => {
        if (isTransitioning) return;
        isTransitioning = true;
        
        index--;
        track.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        track.style.transform = `translateX(-${index * getCardWidth()}px)`;
    });

    track.addEventListener('transitionend', () => {
        isTransitioning = false;

        if (index >= allCards.length - clonesNeeded) {
            track.style.transition = 'none';
            index = clonesNeeded;
            track.style.transform = `translateX(-${index * getCardWidth()}px)`;
        }
        
        if (index === 0) {
            track.style.transition = 'none';
            index = allCards.length - (clonesNeeded * 2);
            track.style.transform = `translateX(-${index * getCardWidth()}px)`;
        }
    });

    window.addEventListener('resize', () => {
        track.style.transition = 'none';
        track.style.transform = `translateX(-${index * getCardWidth()}px)`;
    });
});