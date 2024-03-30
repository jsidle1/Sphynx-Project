// directions
const EMPTY = 0;
const LEFT = 1;
const DOWN = 2;
const UP = 3;
const RIGHT = 4;

// positioning
const LEFT_X = 300;
const UP_X = 400;
const DOWN_X = 500;
const RIGHT_X = 600;
const ARROW_Y = 500;
const SCREEN_HEIGHT = 600;
const SCREEN_WIDTH = 900;

// color hex codes
const HEX_BLUE = 0x5e48ff;
const HEX_RED = 0xca4520;
const HEX_GREEN = 0x87c748;
const HEX_PINK = 0xd969e3;
const HEX_BLACK = 0x000000;

// colors
const BLUE = 1;
const RED = 2;
const GREEN = 3;
const PINK = 4;
const NUM_COLORS = 4;

// animation and bounds
const MS_PER_SECOND = 1000;
const PAINTS_PER_SECOND = 60;
const BEATS_PER_SECOND = 1;
const DROP_FACTOR = 2 * difficulty;
const ROOM_FOR_ERROR = 20;
const ARROW_SIZE = 50;

// game globals
var prevTime = 0;
var prevPaint = 0;
var currStartTime = 0;
var beat = 0;
var currArrows = [];
var currKey = EMPTY;
var currColor = BLUE;
var activeColor = 0;
var score = 0;
var paused = false;

// sscript = [
//     EMPTY, 
//     DOWN, 
//     EMPTY, 
//     RIGHT, 
//     RIGHT, 
//     LEFT, 
//     LEFT, 
//     UP, 
//     LEFT, 
//     UP, 
//     UP, 
//     DOWN,
//     EMPTY, 
//     DOWN, 
//     EMPTY, 
//     RIGHT, 
//     RIGHT, 
//     EMPTY, 
//     LEFT, 
//     EMPTY, 
//     LEFT, 
//     UP, 
//     EMPTY, 
//     DOWN,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY,
//     EMPTY
// ]

// holder for sprite, color, and direction of the arrow
class Arrow{
    constructor(direction, color, sprite)
    {
        this.direction = direction;
        this.color = color;
        this.sprite = sprite;
    }
}

// get position of open arrow from direction
function getX(direction)
{
    switch(direction)
    {
        case LEFT:
            return LEFT_X;
        case RIGHT:
            return RIGHT_X;
        case UP:
            return UP_X;
        case DOWN:
            return DOWN_X;
    }
    return -100;
}

// take direction and color and return sprite texture name
function getSpriteString(direction, color)
{
    let output = '';
    switch(color)
    {
        case BLUE:
            output += 'blue_arrow_';
            break;
        case RED:
            output += 'red_arrow_';
            break;
        case GREEN:
            output += 'green_arrow_';
            break;
        case PINK:
            output += 'pink_arrow_';
            break;
    }
    switch(direction)
    {
        case LEFT:
            output += 'left';
            break;
        case RIGHT:
            output += 'right';
            break;
        case UP:
            output += 'up';
            break;
        case DOWN:
            output += 'down';
            break;
    }

    return output;
}

class Game extends Phaser.Scene
{
    constructor ()
    {
        super();
    }

    preload ()
    {
        // open arrow assets
        this.load.image('arrow_down', 'static/assets/Arrow_Down.png');
        this.load.image('arrow_up', 'static/assets/Arrow_Up.png');
        this.load.image('arrow_left', 'static/assets/Arrow_Left.png');
        this.load.image('arrow_right', 'static/assets/Arrow_Right.png');

        // blue arrow assets
        this.load.image('blue_arrow_down', 'static/assets/Blue_Arrow_down.png');
        this.load.image('blue_arrow_up', 'static/assets/Blue_Arrow_Up.png');
        this.load.image('blue_arrow_left', 'static/assets/Blue_Arrow_Left.png');
        this.load.image('blue_arrow_right', 'static/assets/Blue_Arrow_Right.png');

        // red arrow assets
        this.load.image('red_arrow_down', 'static/assets/Red_Arrow_down.png');
        this.load.image('red_arrow_up', 'static/assets/Red_Arrow_Up.png');
        this.load.image('red_arrow_left', 'static/assets/Red_Arrow_Left.png');
        this.load.image('red_arrow_right', 'static/assets/Red_Arrow_Right.png');

        // green arrow assets
        this.load.image('green_arrow_down', 'static/assets/Green_Arrow_down.png');
        this.load.image('green_arrow_up', 'static/assets/Green_Arrow_Up.png');
        this.load.image('green_arrow_left', 'static/assets/Green_Arrow_Left.png');
        this.load.image('green_arrow_right', 'static/assets/Green_Arrow_Right.png');

        // pink arrow assets
        this.load.image('pink_arrow_down', 'static/assets/Pink_Arrow_down.png');
        this.load.image('pink_arrow_up', 'static/assets/Pink_Arrow_Up.png');
        this.load.image('pink_arrow_left', 'static/assets/Pink_Arrow_Left.png');
        this.load.image('pink_arrow_right', 'static/assets/Pink_Arrow_Right.png');
        
        this.add.text(0,0,'', {fontFamily:'russo', opacity:'0'}); // load font to make sure its downloaded in time
    }

    create ()
    {
        // create open arrows at the bottom of the screen
        this.add.image(LEFT_X, ARROW_Y, 'arrow_left').setScale(0.0625);
        this.add.image(UP_X, ARROW_Y, 'arrow_up').setScale(0.0625);
        this.add.image(DOWN_X, ARROW_Y, 'arrow_down').setScale(0.0625);
        this.add.image(RIGHT_X, ARROW_Y, 'arrow_right').setScale(0.0625);

        // active color text
        this.colorText = this.add.text(0,SCREEN_HEIGHT-40,'colorText', {fontFamily:'russo', fontSize:'40px'});
        this.colorText.text = 'ACTIVE COLOR';
        this.colorText.setTint(HEX_BLUE);
        activeColor = this.colorText;

        // score text
        this.scoreText = this.add.text(SCREEN_WIDTH-100, SCREEN_HEIGHT-40, 'scoreText', {fontFamily:'russo', fontSize:'40px'});
        this.scoreText.setTint(HEX_BLACK);
        this.scoreText.text = '0';

        // pause button
        this.pauseButton = this.add.text(0,40,'pauseText', {fontFamily:'russo', fontSize:'40px'}).setOrigin(0).setInteractive();
        this.pauseButton.setTint(HEX_BLACK);
        this.pauseButton.text = '| |';

        // pause event
        this.pauseButton.on('pointerup', ()=>{
            paused = !paused;
        });
    }

    update (time, delta)
    {
        if(paused)
        {
            prevTime += delta;
            return;
        }

        // update on each beat
        if((time-prevTime) >= (MS_PER_SECOND/BEATS_PER_SECOND))
        {
            if(script[beat] != EMPTY) // if beat exists, get the arrow
            {
                let tcolor = Math.floor(Math.random()*NUM_COLORS)+1; // choose random color
                // push arrow to the front of the array that functions as a queue of arrows (oldest in the back);
                currArrows.unshift(new Arrow(script[beat], tcolor, this.add.sprite(getX(script[beat]), 0, getSpriteString(script[beat], tcolor)).setScale(0.0625)));
            }

            prevTime = time; // update time
            beat++; // update beat

            if(beat>=script.length) // end of script
            {
                $.ajax({
                    type : 'POST',
                    url : scoreUrl,
                    contentType: 'application/json;charset=UTF-8',
                    dataType: 'json',
                    data : JSON.stringify({name:tname, score:score})
                });

                window.location.replace(`${window.location.origin}/levels?name=${name}`);
            }
        }
        
        // update on each paint
        if((time-prevPaint) >= (MS_PER_SECOND/PAINTS_PER_SECOND))
        {
            let toDelete = 0; // variable to determine which arrows are terminated on each paint

            // loop through game objects
            for(const arrow of currArrows)
            {
                arrow.sprite.y += DROP_FACTOR; // move arrow

                // if arrow is in target area and correct direction/color is inputted
                if(arrow.sprite.y > (ARROW_Y-(ARROW_SIZE)) && arrow.sprite.y < (ARROW_Y+(ARROW_SIZE)) && arrow.direction == currKey && arrow.color == currColor)
                {
                    score+=(ARROW_SIZE)-Math.abs(ARROW_Y-arrow.sprite.y); // score updated based on how close it is to target
                    toDelete++; // one arrow will be popped from queue

                    this.scoreText.text = score.toString(); // update score text

                    currKey = EMPTY; // prevent "double key"
                }

                // remove arrows that hit the bottom
                if(arrow.sprite.y >= SCREEN_HEIGHT-ARROW_SIZE)
                {
                    toDelete++;
                }
            }

            // loop through and pop/destroy sprites that are done
            for(let i = 0; i < toDelete; i++)
            {
                currArrows.pop().sprite.destroy(true);
            }

            prevPaint=time; // update time
        }
    }
}

// basic config
const config = {
    type: Phaser.AUTO,
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    autoCenter:true,
    scene: Game,
    backgroundColor: '#FFFFFF'
};

// key presses handled natively
document.addEventListener('keydown', (e) =>{
    if(e.key == 'ArrowLeft')
    {
        currKey = LEFT;
    }
    else if(e.key == 'ArrowRight')
    {
        currKey = RIGHT;
    }
    else if(e.key == 'ArrowUp')
    {
        currKey = UP;
    }
    else if(e.key == 'ArrowDown')
    {
        currKey = DOWN;
    }
    
    else if(e.key == 'a')
    {
        activeColor.setTint(HEX_BLUE);
        currColor = BLUE;
    }
    else if(e.key == 's')
    {
        activeColor.setTint(HEX_RED);
        currColor = RED;
    }
    else if(e.key == 'd')
    {
        activeColor.setTint(HEX_GREEN);
        currColor = GREEN;
    }
    else if(e.key == 'f')
    {
        activeColor.setTint(HEX_PINK);
        currColor = PINK;
    }
});

// prevent keys from staying selected after key press
document.addEventListener('keyup', (e) =>{
    currKey = EMPTY;
});

// instantiate game
const game = new Phaser.Game(config);
